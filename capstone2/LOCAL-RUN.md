# Local Robot Shop rehearsal

This is a local demonstration, not an AWS deployment. The rehearsal uses the
existing `capstone-rollback-lab-control-plane` kind node and separate `robot-shop`
and `observability` namespaces. Never use the default kubeconfig for these commands.
Do not stop unrelated Docker applications or delete the rollback namespace.

## Prerequisites and exact inputs

- Docker Desktop Linux containers; observed allocation 12 CPUs / 7.57 GiB.
- Kubernetes v1.35.0 in the existing local kind cluster; Helm 4.3.1 used.
- Official `kube-prometheus-stack` chart **92.7.0**, downloaded outside Git.
- `robot-images.resolved.yaml` and `images.resolved.yaml` record registry metadata
  resolved for the lab. Resolution alone is not vulnerability/compatibility approval.
- Four focus service builds plus the upstream load generator are local images,
  never registry publications. See their Dockerfiles, dependency locks and smoke
  receipts. Supporting upstream images are legacy and not production approved.
- Private local kubeconfig must live outside Git. Its API URL must be loopback.
  The evidence/incident helper refuses other servers or node names.

The initial install timed out while images were still downloading. This is a
recorded failure, not successful deployment evidence. Obtain current status and
actual traffic/telemetry receipts before declaring readiness.

## Rebuild and import local images

From the repository root, using PowerShell:

```powershell
docker build -t capstone2-web:local capstone2/local-services/web
docker build -t capstone2-payment:local capstone2/local-services/payment
docker build -t capstone2-cart:local capstone2/instrumented/cart
docker build -t capstone2-catalogue:local capstone2/instrumented/catalogue
docker build -t capstone2-loadgen:local capstone2/local-services/loadgen
```

Save/import those five images using Docker's image archive and kind's containerd:

```powershell
$archive = Join-Path $env:TEMP 'capstone2-focus-images.tar'
docker save -o $archive capstone2-web:local capstone2-payment:local capstone2-cart:local capstone2-catalogue:local capstone2-loadgen:local
docker cp $archive capstone-rollback-lab-control-plane:/root/capstone2-focus-images.tar
docker exec capstone-rollback-lab-control-plane ctr -n k8s.io images import /root/capstone2-focus-images.tar
```

Check each native command's exit code. Preserve local image IDs in evidence;
Kubernetes may report the platform/config digest rather than the Docker index ID.
Do not publish these tags. The chart's `localDemo` exception is explicit and for
this rehearsal only; it must not be used in production promotion.

## Installation sequence

Set `$cfg` to the private local kubeconfig. First require exactly the known local
node and confirm the kubeconfig server points to `https://127.0.0.1:<port>`.
Do not print raw kubeconfig credentials or commit the file.

Create only the two lab namespaces. Create `capstone2-grafana` in `observability`
with random local credentials using an in-memory Secret manifest; do not save it
to Git or command history. No Slack webhook was available: the local values use a
receiver without delivery. The separate base values retain the Slack Secret/file
contract; actual Slack delivery remains incomplete.

```powershell
helm --kubeconfig $cfg install monitoring <downloaded-kube-prometheus-stack-92.7.0.tgz> -n observability -f capstone2/monitoring-local.values.yaml --wait --timeout 8m
helm --kubeconfig $cfg install capstone-observability capstone2/observability -n observability -f capstone2/images.resolved.yaml --wait --timeout 8m
helm --kubeconfig $cfg install robot-shop capstone2/robot-shop -n robot-shop -f capstone2/robot-images.resolved.yaml -f capstone2/local-demo.values.yaml --wait --timeout 8m
```

These are first-install commands. For an existing release, inspect status and use
a deliberate upgrade of the same reviewed configuration; never blindly reinstall
or remove storage to resolve a timeout. A failed Helm status with progressing Pods
does not justify deleting them or their databases.

`PAYMENT_GATEWAY` targets Payment's internal `/health` for a simulated gateway.
This is not a real financial transaction. All application Services are ClusterIP;
UI access requires a loopback-bound, explicitly configured port-forward.

## Genuine evidence and controlled incident

After all application and telemetry Pods are healthy:

```powershell
python -B capstone2/local_rehearsal.py --kubeconfig $cfg --evidence <private-or-reviewed-evidence-directory>
```

Inspect returned HTTP statuses and bodies. The helper records results; it does not
turn empty Jaeger data or missing metrics into a passing result. It never reads
Secrets. Keep raw evidence outside Git until reviewed for sensitive data.

Run the actual upstream load generator only against the disposable Robot Shop
namespace. Enable `loadgen.enabled=true` with the same local overlay in a reviewed
upgrade; the Job is bounded to one client/five minutes, active deadline six minutes,
no retries and visible output. Capture the final Locust summary including failures.

The independently designed incident removes only Catalogue's serving replica:

```powershell
python -B capstone2/local_rehearsal.py --kubeconfig $cfg --evidence <incident-directory> --incident
```

It requires a healthy one-replica Catalogue, scales it to zero for approximately
two minutes, captures real probes/alerts, and restores one replica in `finally`.
It never changes a database/PVC or Voting App. SIGKILL or API outage can prevent
restoration: restore `deployment/catalogue` to one replica on this exact local
cluster, verify rollout and actual product HTTP200, and record the interruption.
Do not claim Slack delivery or a full-hour SLO from this short drill.

## Isolation, limits and cleanup

Default kind networking does not enforce NetworkPolicy. The policy manifests are
prepared, but this rehearsal does not prove policy enforcement. Fluent Bit has a
read-only node log mount and can technically read other logs; its configured input
selects only Robot Shop. All data is synthetic. No production credentials enter
this environment.

Stop load generation when testing ends. Do not delete the cluster: it also contains
the completed rollback fixture. No cleanup that deletes databases or PVCs is
authorized by this runbook; retain them pending explicit owner cleanup approval.
Record remaining local resource consumption and never describe a failed/partial
installation as a completed observability demonstration.
