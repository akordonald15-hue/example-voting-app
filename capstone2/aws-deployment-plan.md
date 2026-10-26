# AWS Robot Shop capacity and deployment approval plan

Prepared locally October26,2026. **NO-GO for AWS execution without separate
capacity, spend, downtime and deployment approvals.** No AWS resources, IAM,
security groups, credentials or workloads were changed. Only read-only official
AWS Price List queries were performed for this plan.

## Capacity decision

Owner-supplied node budget:2000m allocatable CPU, approximately3830Mi allocatable
memory; existing requests650m/748Mi. Available before safety allowance:
1350m/3082Mi. Robot Shop's12 service/data-store containers reserve1200m/1956Mi.
Known monitoring main containers reserve425m/704Mi; one load generator adds
50m/64Mi. Combined known reservations: **2325m/3472Mi**, before monitoring
sidecars/operator/exporters and rollout surge. CPU already exceeds capacity;
approximately358Mi memory headroom is inadequate. These are configured requests,
not measured load, and local integration failures are not a capacity benchmark.

Do not lower requests simply to make scheduling succeed. Shipping/MySQL need
startup memory, Prometheus needs WAL/head space, Jaeger/Loki buffers grow with
traffic, and simultaneous image pulls consume disk/CPU. Target4vCPU/16GiB with
an explicit rendered all-container budget and measured peak before AWS deployment.
Budget20–30GiB free disk for images/telemetry as an initial allowance, not a proven
minimum. Do not grow production EBS automatically; EBS growth cannot be undone
by reducing a Terraform variable.

| Option | Capacity/availability consequence | Recommendation |
|---|---|---|
| Existing t3.medium | Unschedulable combined CPU reservations; shared OOM/disk risk to Voting App | NO-GO |
| Resize to t3.large |8GiB helps memory, but still only2vCPU | NO-GO for full declared CPU budget |
| Resize existing node to t3.xlarge |4vCPU/16GiB; whole-cluster stop/start outage, credit sensitivity, same failure domain | Smallest practical same-node demo candidate, separately approved |
| Resize existing node to m7i.xlarge |4vCPU/16GiB, no CPU credit balance, whole-cluster outage | More predictable combined-load candidate |
| Add dedicated m7i.xlarge K3s worker |4vCPU/16GiB for Robot Shop; existing server/Voting data stays in place | Preferred AWS isolation if same-cluster rubric is mandatory and quota allows |
| Continue local kind | No new AWS charge/outage; genuine local evidence already underway | Safest deadline route, disclose same-AWS-cluster deviation |

A worker does not make the single K3s server highly available. Keep Voting App
on its original node; do not drain it or migrate its local-path PostgreSQL claim.
Pin all Robot Shop/observability workloads including their new PVCs to the worker
using a dedicated label/taint and matching affinity/tolerations. Explicitly constrain
DaemonSets so added collectors do not introduce unintended load on production.
Namespaces alone do not enforce node placement or network isolation.

## Verified price assumptions

Official AWS Price List Query API `AmazonEC2`, queried October26 with location
`EU (Ireland)`, Linux, Shared tenancy, no preinstalled software, Used capacity;
OnDemand effective date2026-10-01. USD excluding tax, transfer, discounts/credits.
The API endpoint was us-east-1, but the product region filter was **eu-west-1**.

| Instance | USD/hour |8h compute |24h compute |
|---|---:|---:|---:|
| t3.medium |0.0456 |0.3648 |1.0944 |
| t3.large |0.0912 |0.7296 |2.1888 |
| t3.xlarge |0.1824 |1.4592 |4.3776 |
| m7i.xlarge |0.2247 |1.7976 |5.3928 |

Resize incremental compute versus existing medium: t3.xlarge **+$1.0944/8h**;
m7i.xlarge **+$1.4328/8h**. Adding a worker adds its full price while the medium
continues running: m7i worker **+$1.7976/8h**, plus disk/network/address costs.
One additional public IPv4 costs$0.005/h ($0.04/8h). Do not add public ingress,
NAT Gateway, load balancer or Elastic IP merely for this demo. An egress-capable
public IP with zero public inbound rules differs from exposing services.
If a worker has no public IP, an existing private egress route must already work;
new NAT/endpoints have separate costs and need approval.

EBS/snapshot costs require a quote for the exact approved disk size and retention;
they are intentionally not included in the compute-only totals. Existing disks
remain billable while stopped. No Free Tier or education-credit coverage assumed.

T3.xlarge earns96credits/hour with40% baseline per vCPU (1.6 aggregate sustained
vCPU). Standard mode can throttle after credits drain. Unlimited can incur
$0.05 per surplus vCPU-hour on Linux; do not enable it silently. M7i avoids that
cost/performance uncertainty. Official sources:
[Price List API](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/price-changes.html),
[CPU baseline](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/burstable-credits-baseline-concepts.html),
[EC2/credit pricing](https://aws.amazon.com/ec2/pricing/on-demand/),
[public IPv4 pricing](https://aws.amazon.com/vpc/pricing/).

## Exact approval boundary and safe sequence

1. Approve one option, region/type, maximum duration and dollar ceiling. Worker
   option needs a fresh quota check: prior standard OnDemand quota was5vCPU;
   existing2+new4=6 would exceed that. No quota increase or IAM change is implicit.
2. For resize, approve an explicit whole-cluster outage window (allow15–30minutes
   planning margin, not guaranteed). Approve backup/snapshot scope and costs before
   creating backups. Preserve instance identity, root EBS volume and production
   PVC UID `44527b3d-1dd6-429c-9dca-14afc31f1552`. A snapshot is not a verified
   database restore; record consistency and recovery limits honestly.
3. Prepare a Terraform **plan only** for concrete review. Existing source has
   `delete_on_termination=true` and `user_data_replace_on_change=true`; any
   replacement/destroy of production is STOP. No user-data, disk or networking
   change may be bundled into an instance-type approval. No create-before-destroy
   workaround against the production local-path data.
4. Separate approval of that exact plan is needed for apply. Stop/start retains
   attached EBS data but loses RAM and autoassigned public IPv4; SSM/browser tunnels
   disconnect. Reconnect privately, verify K3s and original PostgreSQL binding,
   then confirm Voting App before any Robot Shop installation. Never force-stop
   or terminate to bypass a failure. [AWS lifecycle behavior](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/how-ec2-instance-stop-start-works.html).
5. Worker option: approve new instance/EBS, private node-to-server/CNI connectivity,
   restricted join-token provisioning and node registration separately. No public
   API port. K3s token must never enter Git/logs or unrestricted user-data. A
   reviewed security-group matrix must allow only required private API/CNI/kubelet
   paths for the actual configured K3s backend; never a broad VPC-wide shortcut.
6. Approve Robot Shop/observability installation as a distinct stage after full
   image/chart digest, source, resource and health review. Reuse tested image bytes;
   do not push local tags to GHCR without separate publication approval. Production
   chart defaults reject localDemo tags. Use `robot-shop`/`observability` namespaces,
   bounded quotas/limits, private services and explicit policies. Do not alter
   `voting-app`, existing Secrets or PostgreSQL storage.
7. Capture genuine readiness, checkout/load, four-service RED, logs, Jaeger, SLO,
   Slack and incident receipts. No automatic rollback. On failure stop traffic,
   inspect the failed release and choose a reviewed correction; do not force replace
   databases/PVCs or silently reset Robot Shop data to make a test pass.

## Recovery and cleanup approvals

Resize reversal requires another stop/start and outage approval. Remove Robot
Shop workloads first under approved scope, prove remaining reservations fit the
medium, preserve production volumes, then review a type-only reversal plan. Never
downsize with an overloaded scheduler or assume memory is reclaimed automatically.

For an added worker, preserve/export required local evidence and decide disposition
of **only Robot Shop** new PVCs before node removal. Those claims are node-bound;
removing the worker is not database migration. Uninstall only inventoried demo
releases, remove only its node registration/cloud resources after approval, leave
shared CRDs and production resources intact. No cleanup/destroy execution is
authorized by this document.

## Capstone1 push-to-deploy limitations

The current source workflow uses separate `CAPSTONE_PUBLISH_ENABLED` and
`CAPSTONE_DEPLOY_ENABLED` conditions, deploy depends on publish and uses a private
runner label. It is not safe to activate just by setting a variable: public-repo
untrusted workflows must have no scheduling route to a production-capable runner.
Labels are not an isolation boundary. The local private-promotion proposal is
manual artifact promotion of one fixed published release, not proof of automatic
deployment on future source pushes.

Implementable local checks: Actionlint/ShellCheck; guard tests proving disabled
defaults; positive/negative artifact-provenance and digest validation; image-only
Helm render/drift tests; PVC/backend identity tests; failure paths proving no
automatic retry/rollback; sanitized evidence allowlist tests. These can be run
without a production connection. They do not prove real runner/RBAC/pull access.

Before automatic delivery, separately approve a trusted private deployment boundary,
protected environment/branch with plan-compatible reviewer enforcement, scoped
cross-repo source/artifact access, short-lived namespace Kubernetes credentials,
existing GHCR pull reference and independently verified manifests. Helm release
Secret access can expose namespace credentials; plain broad Secret permissions
must not be mislabeled least privilege. Retain image-only drift/PVC guards and
explicit deployment approval. Review stale action pins against published main
before enabling anything; the local feature workflow is not proof of remote main.
No CI variable, runner or production access was enabled by this assessment.
