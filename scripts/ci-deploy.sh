#!/usr/bin/env bash
# Only the approval-gated trusted-main private deployment job calls this script.
set -euo pipefail
umask 077
# Preserve only nonsecret status/identity receipts if Helm fails or disconnects.
# Never upload stored manifests, kubeconfig, Secret objects or arbitrary logs.
mkdir -p deployment-evidence
test -z "${PYTHONOPTIMIZE:-}"
test -n "${CAPSTONE_EXPECTED_PVC_UID:-}"
test -n "${KUBECONFIG:-}" && test -f "$KUBECONFIG"
test "${GITHUB_EVENT_NAME:-}" = push
test "${GITHUB_REF:-}" = refs/heads/main
command -v helm >/dev/null
command -v kubectl >/dev/null
python3 -c 'import yaml'
python3 -c 'import os,yaml; d=yaml.safe_load(open("values.ci.yaml")); assert set(d)=={"components","database","imagePullSecrets","options"}; assert set(d["components"])=={"vote","result","worker","redis","postgres"}; assert all(d["components"][r]["image"]["tag"]==os.environ["GITHUB_SHA"] for r in ("vote","result","worker"))'
work=$(mktemp -d)
trap 'rm -rf -- "$work"' EXIT
chmod 700 "$work"
helm status capstone -n voting-app -o json > "$work/status.json"
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); print(json.dumps({"name":d["name"],"namespace":d["namespace"],"version":d["version"],"status":d["info"]["status"]}))' "$work/status.json" > deployment-evidence/status-before.json
python3 -c 'import json,sys; assert json.load(open(sys.argv[1]))["info"]["status"] == "deployed"' "$work/status.json"
kubectl wait --for=condition=Ready pod -n voting-app -l app.kubernetes.io/instance=capstone --timeout=60s
# This chart has external Secret references only. Never export Kubernetes Secret objects.
helm get manifest capstone -n voting-app > "$work/before.yaml"
helm template capstone helm/voting-app -n voting-app --is-upgrade --kube-version 1.36.5 -f values.ci.yaml > "$work/after.yaml"
python3 scripts/ci-check-render.py "$work/before.yaml" "$work/after.yaml"
kubectl get pvc data-capstone-voting-app-postgres-0 -n voting-app -o json > "$work/pvc-before.json"
python3 scripts/ci-check-pvc.py "$work/pvc-before.json" "$CAPSTONE_EXPECTED_PVC_UID" > "$work/pvc-before"
cp "$work/pvc-before" deployment-evidence/pvc-before.json
set +e
helm upgrade capstone helm/voting-app -n voting-app -f values.ci.yaml --wait --timeout 10m
upgrade_status=$?
set -e
printf '%s\n' "$upgrade_status" > deployment-evidence/upgrade-exit-code.txt
if [ "$upgrade_status" -ne 0 ]; then
  printf '%s\n' 'STOP: upgrade failed or outcome uncertain; inspect before any retry or rollback.' >&2
  exit "$upgrade_status"
fi
kubectl get pvc data-capstone-voting-app-postgres-0 -n voting-app -o json > "$work/pvc-after.json"
python3 scripts/ci-check-pvc.py "$work/pvc-after.json" "$CAPSTONE_EXPECTED_PVC_UID" > "$work/pvc-after"
cp "$work/pvc-after" deployment-evidence/pvc-after.json
cmp "$work/pvc-before" "$work/pvc-after"
kubectl get pods -n voting-app -l app.kubernetes.io/instance=capstone -o json > "$work/pods-after.json"
python3 scripts/ci-check-running.py values.ci.yaml "$work/pods-after.json" > deployment-evidence/running.json
helm status capstone -n voting-app
kubectl get pods,pvc -n voting-app
# No automatic rollback: preserve evidence and investigate a failed/uncertain operation.
