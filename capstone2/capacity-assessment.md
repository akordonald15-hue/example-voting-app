# Capacity assessment — 2026-10-26

**NO-GO for deployment. Read-only assessment; no configuration changes.**

AWS describe-instances confirms running t3.medium; describe-instance-types confirms
2 vCPU / 4096MiB. The reported 8GiB corresponds to t3.large, not this instance.
Credit specification is Standard. Latest returned hourly CPUCreditBalance samples
through 2026-10-26 02:00 UTC have minimum/average 576. This is historical credit
evidence, not proof of current Kubernetes capacity or future peak performance.

## Budget

CPU units m, memory Mi. Requests are scheduler reservations, limits are configured
ceilings, neither is a measurement of steady or peak consumption.

| Component | Request CPU/memory | Limit CPU/memory |
|---|---:|---:|
| Voting App, five containers | 450 / 608 | 2250 / 1216 |
| Robot Shop, twelve containers | 1200 / 1956 | 2400 / 3536 |
| Blackbox | 50 / 64 | 500 / 64 |
| Loki | 50 / 64 | 500 / 512 |
| Jaeger | 50 / 64 | 500 / 256 |
| OTEL | 50 / 64 | 500 / 128 |
| Fluent Bit, one node | 50 / 32 | 200 / 96 |
| Prometheus | 100 / 256 | 500 / 512 |
| Grafana main container | 50 / 128 | 250 / 256 |
| Alertmanager main container | 25 / 32 | 100 / 64 |
| Known steady configuration subtotal | **2075 / 3268** | **7700 / 6640** |
| Load generation, one client | 50 / 64 | 200 / 128 |
| Known loaded subtotal | **2125 / 3332** | **7900 / 6768** |

Missing from these subtotals: live system pods, operator, node exporter,
kube-state-metrics, Grafana dashboard/datasource sidecars, Prometheus/Alertmanager
config reloaders, admission installation jobs, initialization and rollout surge.
The official monitoring chart is not yet pinned/rendered. Therefore a complete
measured peak or final chart-derived total is **UNKNOWN**, not 2075m.
Storage also needs accounting: Prometheus WAL/head beyond 512MB retention target,
Loki chunks/index, container images, host logs, ephemeral buffers and existing
database growth. Small emptyDir quotas may stop telemetry before node exhaustion.

For capacity planning ONLY, reserve an additional 300m/512Mi for monitoring
support containers and 500m/1024Mi for K3s/OS/system workloads. Loaded envelope
then becomes approximately **2925m / 4868Mi**, before startup/surge and 25%
headroom. These are explicit allowances, not observed usage or tested minima.
Do not double-count system pods when replacing allowances with actual evidence.
Budget startup/surge separately from maximum concurrent replicas and init-container
resources in the final rendered chart. All configured CPU limits may exceed node
capacity; aggregate memory ceilings below safe capacity are preferable for this lab.

## Options

- Existing 2CPU/4GiB: not feasible as declared. Lowering requests to make pods
  schedule does not reduce actual memory/CPU. No compliant safe low-resource
  configuration is proven. Retain all mandatory components; first profile locally
  at one load client, bound telemetry cardinality/retention, tune JVM heaps and
  requests using measurements, then retest startup and incident recovery.
- t3.large, 2CPU/8GiB: memory improvement but identical CPU count; does not fit
  existing requests, and only 0.6 sustained vCPU baseline. Not recommended.
- t3.xlarge, 4CPU/16GiB: plausible short lab candidate, 1.6 sustained vCPU baseline;
  sustained combined workloads can still drain credits/throttle in Standard mode.
- m7i.xlarge, 4CPU/16GiB: preferred predictable candidate without CPU credits.
  Final GO still requires measured allocatable, full chart budget and rehearsal.

Indicative Linux eu-west-1 on-demand prices, USD excluding EBS/tax/transfer:
t3.medium $0.0456/h ($33.29/730h); t3.large $0.0912/h ($66.58);
t3.xlarge $0.1824/h ($133.15); m7i.xlarge $0.2247/h ($164.03).
Ten hours costs approximately $0.46/$0.91/$1.82/$2.25 respectively.
Confirm the AWS quote before approval; these are estimates, not a purchase.
Sources: https://cloudparity.io/pricing/aws/t3.medium,
https://cloud-credits.org/prices/ec2/t3-large/eu-west-1,
https://cloudparity.io/pricing/aws/t3.xlarge,
https://cloud.cloudquell.com/aws/ec2/m7i.xlarge/.
Credit baseline and Linux Unlimited surplus rate ($0.05/vCPU-hour):
https://aws.amazon.com/ec2/instance-types/t3/.
Requests do not consume credits; actual CPU execution does. At sustained 100%
CPU a medium spends 120 credits/h and earns 24: a full 576 balance lasts about
6 hours before Standard throttling (idealized, constant load). Do not switch
credit mode implicitly or assume the current balance carries across a resize.

## Missing live evidence — existing owner SSM Linux shell

These commands are read-only; no Secret objects or credential contents requested.

```sh
sudo -n k3s kubectl get nodes -o custom-columns=NAME:.metadata.name,CPU:.status.allocatable.cpu,MEMORY:.status.allocatable.memory,DISK:.status.allocatable.ephemeral-storage
```
```sh
sudo -n k3s kubectl describe node ip-172-31-25-57
```
The second includes allocated request/limit totals, pod list and pressure conditions.

```sh
sudo -n k3s kubectl get pods -A -o custom-columns='NS:.metadata.namespace,POD:.metadata.name,CPU_REQ:.spec.containers[*].resources.requests.cpu,MEM_REQ:.spec.containers[*].resources.requests.memory,CPU_LIM:.spec.containers[*].resources.limits.cpu,MEM_LIM:.spec.containers[*].resources.limits.memory,INIT_REQ:.spec.initContainers[*].resources.requests,OVERHEAD:.spec.overhead'
```
```sh
sudo -n k3s kubectl top pods -A --containers
```
```sh
sudo -n k3s kubectl top nodes
```
```sh
df -h /var/lib/rancher/k3s
```
Metrics unavailable means UNKNOWN. A snapshot is insufficient for measured peak;
sample during a separately approved rehearsal, startup and load/incident tests.

## Preservation and decision

Recommend separately reviewing an in-place x86 m7i.xlarge resize with the same
instance/root EBS and local-path directory, rather than replacing the node or
adding complexity to squeeze into 4GiB. Stop/start entails application downtime
and Redis emptyDir loss is possible; do not call it nondisruptive. Require an
approved PostgreSQL backup/restore validation, storage identity receipt, capacity/
AZ/type compatibility, maintenance window, AWS cost approval and Terraform plan
review that rejects replacement/destruction of the instance or disk. Rollback is
an approved type reversal preserving EBS, never PVC deletion. No resize commands
are authorized by this assessment. Preserve the running application meanwhile.

Final status: AWS hardware/credit evidence PASS; declared current fit FAIL;
actual allocatable/live requests UNKNOWN; measured peak UNKNOWN; fully rendered
monitoring budget UNKNOWN. No deployment or resize GO until those gates close.
