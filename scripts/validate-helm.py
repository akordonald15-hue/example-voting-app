"""Offline Helm rendering/contract checks. Requires Helm and PyYAML, never kubectl."""
import argparse
from pathlib import Path
import subprocess

import yaml

ROOT = Path(__file__).resolve().parents[1]
CHART = ROOT / "helm/voting-app"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--helm", default="helm")
    parser.add_argument("--values", type=Path, help="Optional release-specific values overlay")
    args = parser.parse_args()

    def helm(*flags, ok=True):
        if args.values:
            flags = (*flags, "--values", str(args.values))
        if flags[0] == "template" and "--kube-version" not in flags:
            flags = (*flags, "--kube-version", "1.36.5")
        result = subprocess.run([args.helm, *map(str, flags)], capture_output=True, text=True)
        if ok and result.returncode:
            raise AssertionError(result.stderr + result.stdout)
        if not ok:
            assert result.returncode != 0, "Invalid configuration unexpectedly rendered"
        return result.stdout

    helm("lint", CHART, "--strict")
    for release in ["capstone", "second-release", "a" * 43 + "-first", "a" * 43 + "-second"]:
        command = ("template", release, CHART, "--namespace", "voting-app", "--kube-version", "1.36.5")
        rendered = helm(*command)
        assert rendered == helm(*command), "Render must be deterministic"
        documents = list(yaml.safe_load_all(rendered))
        assert len(documents) == 17
        workloads = [d for d in documents if d["kind"] in ["Deployment", "StatefulSet"]]
        assert len(workloads) == 5
        assert len([d for d in documents if d["kind"] == "StatefulSet"]) == 1
        assert len([d for d in documents if d["kind"] == "NetworkPolicy"]) == 7
        assert not any(d["kind"] in ["Secret", "Ingress", "ClusterRole", "Namespace"] for d in documents)
        assert not any(k in rendered for k in ["hostNetwork:", "nodePort:", "privileged: true"])
        pods = {}
        requests = limits = 0
        for d in workloads:
            spec = d["spec"]["template"]["spec"]
            labels = d["spec"]["template"]["metadata"]["labels"]
            role = labels["app.kubernetes.io/component"]
            pods[role] = labels
            assert d["spec"]["replicas"] == 1
            assert spec["automountServiceAccountToken"] is False
            assert spec["securityContext"]["runAsNonRoot"] is True
            assert spec["securityContext"]["runAsUser"] > 0
            assert spec["securityContext"]["seccompProfile"]["type"] == "RuntimeDefault"
            container = spec["containers"][0]
            sec = container["securityContext"]
            assert sec["readOnlyRootFilesystem"] and not sec["allowPrivilegeEscalation"]
            assert sec["capabilities"]["drop"] == ["ALL"]
            assert container.get("startupProbe") and container.get("readinessProbe")
            assert ":latest" not in container["image"]
            if role == "worker":
                assert "livenessProbe" not in container, "Dependency outages must not cause restart loops"
            else:
                assert container.get("livenessProbe")
            for env in container.get("env", []):
                if env["name"] in ["PGPASSWORD", "POSTGRES_PASSWORD"]:
                    assert "secretKeyRef" in env["valueFrom"] and "value" not in env
            requests += int(container["resources"]["requests"]["memory"][:-2])
            limits += int(container["resources"]["limits"]["memory"][:-2])
        assert requests == 608 and limits == 1216
        for service in [d for d in documents if d["kind"] == "Service"]:
            assert service["spec"]["type"] == "ClusterIP"
            selector = service["spec"]["selector"]
            assert any(all(labels.get(k) == v for k, v in selector.items()) for labels in pods.values())
        pg = next(d for d in workloads if d["kind"] == "StatefulSet")
        assert pg["spec"]["persistentVolumeClaimRetentionPolicy"] == {"whenDeleted": "Retain", "whenScaled": "Retain"}
        claim = pg["spec"]["volumeClaimTemplates"][0]
        assert claim["spec"]["storageClassName"] == "local-path"
        assert claim["spec"]["resources"]["requests"]["storage"] == "2Gi"
        config = next(d for d in documents if d["kind"] == "ConfigMap")["data"]
        names = {d["metadata"]["name"] for d in documents if d["kind"] == "Service"}
        assert config["PGHOST"] in names and config["REDIS_HOST"] in names
        print(f"PASS {release}: 5 workloads, 4 ClusterIP services, 7 policies; 608Mi requested/1216Mi limited")

    # A tag is irrelevant when a valid digest is set. Clear it only for this
    # tag-only negative case; the published overlay intentionally pins digests.
    for flags in [
        ["--set", "components.vote.image.tag=latest", "--set-string", "components.vote.image.digest="],
        ["--set", "components.worker.image.digest=sha256:bad"],
        ["--set", "database.storageSize=0Gi"],
        ["--set", "database.password=forbidden"],
        ["--set", "components.typo.image.tag=unexpected"],
        ["--set-string", "components.vote.resources.requests.cpu=0"],
    ]:
        helm("template", "bad", CHART, *flags, ok=False)
    print("PASS negative values/schema tests")
    digest = "sha256:" + "a" * 64
    rendered = helm("template", "digest", CHART, "--set", "components.vote.image.digest=" + digest)
    assert "example-voting-app-vote@" + digest in rendered
    print("PASS digest image override")
    long_names = []
    for suffix in ["-first", "-second"]:
        docs = yaml.safe_load_all(helm("template", "a" * 43 + suffix, CHART))
        long_names.append(next(d["metadata"]["name"] for d in docs if d["kind"] == "Service"))
    assert long_names[0] != long_names[1], "Long releases must not collide after truncation"
    print("PASS long-release name collision prevention")


if __name__ == "__main__":
    main()
