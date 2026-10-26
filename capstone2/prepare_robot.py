"""Fetch a pinned upstream snapshot and prepare a namespace-guarded chart locally.

No Kubernetes/Docker/AWS commands. Source images still need review, scans and pins.
"""
import hashlib
import json
from pathlib import Path
import re
import urllib.request

COMMIT = "55292e2199f2fb00a165b1f7d3045fe7f8922038"
ROOT = Path(__file__).resolve().parent
BASE = f"https://raw.githubusercontent.com/instana/robot-shop/{COMMIT}/"

def fetch(path):
    with urllib.request.urlopen(BASE + path, timeout=30) as response:
        return response.read()

def main():
    with urllib.request.urlopen(f"https://api.github.com/repos/instana/robot-shop/git/trees/{COMMIT}?recursive=1", timeout=30) as response:
        tree = json.load(response)["tree"]
    paths = [x["path"] for x in tree if x["type"] == "blob" and
             (x["path"].startswith("K8s/helm/") or x["path"].startswith("load-gen/") or
              x["path"] in {f"{r}/{f}" for r in ("cart", "catalogue") for f in ("server.js", "package.json", "Dockerfile")} or
              x["path"].upper() in ("LICENSE", "LICENSE.TXT"))]
    excluded = {"clusterrole.yaml", "clusterrolebinding.yaml", "podsecuritypolicy.yaml", "serviceaccount.yaml"}
    receipt = {"repository": "https://github.com/instana/robot-shop", "commit": COMMIT, "files": {}}
    for path in paths:
        raw = fetch(path)
        receipt["files"][path] = hashlib.sha256(raw).hexdigest()
        if path.startswith("K8s/helm/"):
            relative = path.removeprefix("K8s/helm/")
            if Path(relative).name in excluded:
                continue
            destination = ROOT / "robot-shop" / relative
            text = raw.decode()
            if relative.startswith("templates/") and ("deployment" in relative or "statefulset" in relative):
                role = Path(relative).name.replace("-deployment.yaml", "").replace("-statefulset.yaml", "")
                text = re.sub(r'^([ ]*)image:.*$', lambda m: m[1] + 'image: {{ include "robot.image" (dict "root" . "name" "' + role + '") }}', text, flags=re.M)
                text = re.sub(r'        env:\n          - name: INSTANA_AGENT_HOST\n            valueFrom:\n              fieldRef:\n                fieldPath: status.hostIP\n', '', text)
                text = re.sub(r'          - name: INSTANA_AGENT_HOST\n            valueFrom:\n              fieldRef:\n                fieldPath: status.hostIP\n', '', text)
                text = re.sub(r'        {{- if .Values.eum.key }}.*?        {{- end}}\n', '', text, flags=re.S)
                text = text.replace('      {{ if .Values.psp.enabled }}\n      serviceAccountName: robot-shop\n      {{ end }}\n', '')
                text = text.replace('    spec:\n', '    spec:\n      automountServiceAccountToken: false\n', 1)
                if role in ("cart", "catalogue"):
                    marker = '        imagePullPolicy: {{ .Values.image.pullPolicy }}\n'
                    text = text.replace(marker, marker + '        env:\n' +
                        f'          - {{name: OTEL_SERVICE_NAME, value: {role}}}\n' +
                        '          - {name: OTEL_EXPORTER_OTLP_ENDPOINT, value: "http://otel.observability.svc.cluster.local:4318"}\n' +
                        '          - {name: OTEL_EXPORTER_OTLP_PROTOCOL, value: http/protobuf}\n' +
                        '          - {name: OTEL_TRACES_SAMPLER, value: always_on}\n')
                text = text.replace('        # agent networking access\n', '')
            if relative == "values.yaml":
                text = text.replace('storageClassName: standard', 'storageClassName: local-path')
                text += '\n# No mutable upstream image may be deployed. Supply reviewed repository@sha256 pins.\nimages: {}\nloadgen:\n  enabled: false\n'
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_text(text, encoding="utf-8")
        else:
            destination = ROOT / "upstream-source" / path
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)
    helpers = ROOT / "robot-shop/templates/_capstone.tpl"
    helpers.write_text('''{{- define "robot.image" -}}
{{- if ne .root.Release.Namespace "robot-shop" }}{{ fail "STOP: Robot Shop namespace only" }}{{ end }}
{{- if or .root.Values.nodeport .root.Values.ocCreateRoute }}{{ fail "STOP: public exposure is not approved" }}{{ end }}
{{- $ref := required (printf "review and pin Robot Shop image %s" .name) (index .root.Values.images .name) }}
{{- if not (regexMatch "^[a-z0-9./:_-]+@sha256:[a-f0-9]{64}$" $ref) }}{{ fail "immutable image required" }}{{ end }}
{{- $ref | quote -}}
{{- end -}}
''', encoding="utf-8")
    (ROOT / "upstream-receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    print("PREPARED LOCAL SNAPSHOT; images and embedded instrumentation remain review gates")

if __name__ == "__main__":
    main()
