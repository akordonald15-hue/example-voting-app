"""Offline rendering contracts. Zero-digest fixtures are never deployment values."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
import yaml

ROOT = Path(__file__).resolve().parent
HELM = os.environ.get("CAPSTONE_HELM", "helm")

class ConfigurationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        values = yaml.safe_load((ROOT / "observability/values.yaml").read_text())
        for image in list(values["components"].values()) + [values["fluentbit"]]:
            image["digest"] = "sha256:" + "0" * 64
        self.fixture = Path(self.temp.name) / "fixture.yaml"
        self.fixture.write_text(yaml.safe_dump(values))

    def render(self, namespace="observability", fixture=True):
        command = [HELM, "template", "capstone-observability", str(ROOT / "observability"), "-n", namespace]
        if fixture:
            command += ["-f", str(self.fixture)]
        return subprocess.run(command, capture_output=True, text=True, timeout=30)

    def test_robot_local_render_is_private_and_bounded(self):
        values = {"images": {name: "example.invalid/" + name + "@sha256:" + "0"*64
                  for name in ("web","catalogue","cart","payment","user","shipping","ratings","dispatch","mongodb","mysql","rabbitmq","redis")}}
        fixture = Path(self.temp.name) / "robot.yaml"
        fixture.write_text(yaml.safe_dump(values))
        result = subprocess.run([HELM,"template","robot-shop",str(ROOT/"robot-shop"),"-n","robot-shop","-f",str(fixture)],capture_output=True,text=True,timeout=30)
        self.assertEqual(result.returncode,0,result.stderr)
        docs=list(yaml.safe_load_all(result.stdout))
        self.assertEqual(sum(d["kind"] in ("Deployment","StatefulSet") for d in docs),12)
        for d in docs:
            if d["kind"]=="Service": self.assertNotIn(d["spec"].get("type","ClusterIP"),("LoadBalancer","NodePort"))
            if d["kind"] in ("Deployment","StatefulSet"):
                pod=d["spec"]["template"]["spec"]
                self.assertFalse(pod["automountServiceAccountToken"])
                for c in pod["containers"]:
                    self.assertIn("requests",c["resources"])
                    self.assertNotIn("NET_ADMIN",c.get("securityContext",{}).get("capabilities",{}).get("add",[]))

    def test_no_unpinned_default_render(self):
        self.assertNotEqual(self.render(fixture=False).returncode, 0)

    def test_cannot_target_voting_app(self):
        self.assertNotEqual(self.render(namespace="voting-app").returncode, 0)

    def test_private_bounded_stack(self):
        result = self.render()
        self.assertEqual(result.returncode, 0, result.stderr)
        docs = list(yaml.safe_load_all(result.stdout))
        self.assertEqual(sum(d["kind"] == "Deployment" for d in docs), 4)
        self.assertFalse(any(d["kind"] in ("Secret", "PersistentVolume", "PersistentVolumeClaim", "Ingress", "ClusterRole", "ClusterRoleBinding") for d in docs))
        for d in docs:
            if d["kind"] == "Service":
                self.assertEqual(d["spec"]["type"], "ClusterIP")
            if d["kind"] in ("Deployment", "DaemonSet"):
                spec = d["spec"]["template"]["spec"]
                self.assertFalse(spec["automountServiceAccountToken"])
                for c in spec["containers"]:
                    self.assertIn("@sha256:", c["image"])
                    self.assertFalse(c["securityContext"]["allowPrivilegeEscalation"])

    def test_configuration_links(self):
        configs = {p.name: yaml.safe_load(p.read_text()) for p in (ROOT / "observability/config").glob("*.yaml")}
        self.assertEqual(configs["otel.yaml"]["exporters"]["otlphttp/jaeger"]["endpoint"], "http://jaeger:4318")
        dashboard = json.loads((ROOT / "observability/dashboards/robot-shop.json").read_text())
        self.assertEqual(len(dashboard["panels"]), 7)
        stack = yaml.safe_load((ROOT / "kube-prometheus-stack.values.yaml").read_text())
        self.assertEqual(stack["grafana"]["admin"]["existingSecret"], "capstone2-grafana")

    def test_blackbox_is_a_required_service_dependency(self):
        docs = list(yaml.safe_load_all(self.render().stdout))
        services = {d["metadata"]["name"]: d for d in docs if d["kind"] == "Service"}
        self.assertEqual(services["blackbox"]["spec"]["ports"][0]["port"], 9115)
        stack = yaml.safe_load((ROOT / "kube-prometheus-stack.values.yaml").read_text())
        probe = stack["prometheus"]["prometheusSpec"]["additionalScrapeConfigs"][0]
        self.assertEqual(probe["params"]["module"], ["http_success"])
        self.assertEqual(probe["relabel_configs"][-1]["replacement"], "blackbox.observability.svc.cluster.local:9115")
        blackbox = yaml.safe_load((ROOT / "observability/config/blackbox.yaml").read_text())
        self.assertIn("http_success", blackbox["modules"])

    def test_slack_secret_mount_contract(self):
        stack = yaml.safe_load((ROOT / "kube-prometheus-stack.values.yaml").read_text())
        alert = stack["alertmanager"]
        self.assertEqual(alert["alertmanagerSpec"]["secrets"], ["capstone2-slack"])
        slack = alert["config"]["receivers"][0]["slack_configs"][0]
        self.assertEqual(slack["api_url_file"], "/etc/alertmanager/secrets/capstone2-slack/webhook")
        self.assertNotIn("api_url", slack)

    def test_trace_receiver_service_contract(self):
        docs = list(yaml.safe_load_all(self.render().stdout))
        jaeger = next(d for d in docs if d["kind"] == "Service" and d["metadata"]["name"] == "jaeger")
        self.assertIn(4318, [p["port"] for p in jaeger["spec"]["ports"]])
        config = yaml.safe_load((ROOT / "observability/config/jaeger.yaml").read_text())
        self.assertEqual(config["receivers"]["otlp"]["protocols"]["http"]["endpoint"], "0.0.0.0:4318")

    def test_log_mount_and_selection(self):
        docs = list(yaml.safe_load_all(self.render().stdout))
        daemon = next(d for d in docs if d["kind"] == "DaemonSet")
        spec = daemon["spec"]["template"]["spec"]
        logs = next(v for v in spec["volumes"] if v["name"] == "logs")
        self.assertEqual(logs["hostPath"], {"path": "/var/log/pods", "type": "Directory"})
        mount = next(v for v in spec["containers"][0]["volumeMounts"] if v["name"] == "logs")
        self.assertTrue(mount["readOnly"])
        config = next(d for d in docs if d["kind"] == "ConfigMap" and d["metadata"]["name"] == "fluent-bit-config")["data"]
        self.assertIn("Path /var/log/pods/robot-shop_*/*/*.log", config["fluent-bit.conf"])
        self.assertIn("service=$service,level=$level", config["fluent-bit.conf"])

if __name__ == "__main__":
    unittest.main()
