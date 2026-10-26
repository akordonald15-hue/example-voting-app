# Reviewed worker expansion — approval required

Prepared2026-10-26; no apply, agent join, permission grant or AWS workload change.
This is a separate Terraform root/state. Never use the production root for cleanup.

## Exact saved plan

Private saved plan (outside Git):
`C:/Users/akord/Desktop/devops-capstone-remediation/worker-expansion/worker.tfplan`

SHA256: `1636bd967c9e7bedc310b53ed5bd9ece45baf8b0aa83c4e06e7b7f8d846aab2d`.
Terraform reports **17 add,0 change,0 destroy**. Despite the zero-change count,
five new rules attach to the existing server security group: three ingress and
two egress. This is an intentional, separately approved production-network change.
No server instance, root disk, PostgreSQL PVC, subnet, route table or IAM role is
managed by this root. No token/password/kubeconfig is in configuration or plan.

Creates:
- One `m7i.xlarge` worker (4vCPU/16GiB), pinned existing Canonical Ubuntu24.04
  amd64 AMI, existing default subnet in eu-west-1a, same VPC as server.
- New encrypted50GiB gp3 root disk (part of instance), IMDSv2/hop-limit1,
  public IPv4 for outbound bootstrap/SSM only, no SSH key or public ingress.
- Dedicated worker security group and15individual rules. HTTPS/HTTP outbound,
  resolver DNS and Amazon Time Sync plus private node-to-node rules only.
- Reuses existing SSM-only instance profile; no new IAM role or permissions.

Private node paths: worker to serverTCP6443; VXLANUDP8472both ways;
metrics/kubeletTCP10250both ways. Rules reference security groups, not public
CIDRs. No2379/2380,NodePort range,SSH or public6443. Server network/firewall
compatibility still requires live review before joining; no production restart.

## Live read-only findings

Existing server remains running t3.medium/SSMOnline; default subnet has4090free
addresses, same VPC, eu-west-1a, active internet-gateway default route. m7i.xlarge
and t3.xlarge are offered in that AZ (offering is not a capacity reservation).
Standard-instance quota is now32vCPU; only the2vCPU server was running.
Existing server group has no inbound rules. Existing role has only
AmazonSSMManagedInstanceCore. Project tag remains devops-capstone-k3s to preserve
existing scoped Session Manager access. Worker identity is its Name tag and
separate state. Do not concurrently apply the production Terraform root.

## Cost and credits

Official Price List: m7i.xlarge$0.2247/hour; gp3$0.088/GB-month; public IPv4
$0.005/hour.50GiB disk=$4.40/month. At730hours/month: **$172.08/month**, or
approximately **$0.23573/hour** before tax/transfer.24hours approximately$5.66.
Propose a **$10gross incremental allowance**, including$4.34contingency, and
review/stop at24hours or October27at10:00UTC (11AMWAT), whichever comes first.
This is comfortably below the owner's$50limit. NoNAT,loadbalancer,EIP or paid
SSM endpoints are created. Cross-AZ placement is not proposed. Monitor transfer;
re-estimate and stop for approval if projected incremental spend exceeds$50.
A tag is not an automatic shutdown or billing cap. Stopped compute retains
billable EBS, and cleanup requires its own approved data-retention decision.

Free Tier API returned ACTIVE/PAID and **$111.93remaining credits**. CostExplorer
October1–26 estimated$8.067575141usage,$-8.067575141credits,net$0. Neither response
establishes expiration or product coverage. Confirm those under BillingCredits;
do not assume credits cover future charges. Gross estimate does not rely on them.

## Concrete IAM blockers — no grant performed

Contextual simulation and policy inspection found:
- m7i.xlarge launch:implicitDeny; allowed instance type currently t3.medium only.
-50GiB new volume:implicitDeny; encryptedgp3 cap currently30GiB.
-PrivateSG ingress creation:implicitDeny; existing policy grants egress only.
-PassRole for the existing project role to ec2.amazonaws.com:allowed.

Administrator must approve narrowly scoped m7i.xlarge launch, new encrypted50GiB
gp3 root volume and creation/revocation/tagging of only the reviewed private
security-group rules. Retain existing AMI/subnet/region/project/IMDSv2 conditions;
no AdministratorAccess, unboundedPassRole or SendCommand request. Re-simulate
concrete resources and re-plan if configuration changes. A plan does not prove
write permissions, EC2 capacity or successful bootstrap.

## Separate execution approvals and join

1.Approve this exact17-resource plan, five existing-server SG rule additions,
$10gross/24h allowance and the narrowly scoped administrator permission update.
No apply until effective permissions are verified and plan remains current.
2.After worker creation, approve joining it. Bootstrap downloads the same pinned
K3s1.36.5+k3s1binary/hash as the server source, prepares SSM and a disabled agent
unit. It does not contain a token or start/join the agent. Verify live server
version/CNI/CIDRs and host firewall before join. Do not disable firewall globally.
3.Provision a reviewed agent/bootstrap credential through private authenticated
SSM handling, into root-owned0600`/etc/rancher/k3s/agent-token`; never user-data,
Terraform,Git,terminal output or public artifacts. Prefer short-lived bootstrap
credentials after reviewing restart/expiry behavior. Do not expose server token.
4.Enable/start the prepared agent only under join approval. It registers with
label`capstone-workload=robot-shop` and matchingNoScheduletaint. Verify Ready,
private routes,DNS, cross-node networking and bounded resource usage. No server
drain/restart and no Voting App replica movement. The existing single server
remains a control-plane availability dependency.
5.Separately approve RobotShop/observability deployment with explicit worker
nodeSelector and matching toleration on EVERYPod (including monitoring/DaemonSets,
Jobs and data stores). Render and total all main/sidecar/init requests first.
Namespace alone is not placement isolation. Verify VotingPostgreSQLPVCUID
44527b3d-1dd6-429c-9dca-14afc31f1552remains unchanged; do not operate on its data.
No production-capable CIrunner on the public source repository.

## Failure handling and cleanup

Stop on permission/bootstrap/network/join failure; no retries that create extra
instances. Keep separate state and logs privately. Never run destroy from
`terraform/`. Before any worker teardown, inventory worker-bound Pods/PVCs/PVs
and approve their retention/export; do not delete databases or persistent data.
If data retention is unresolved, stop the worker under explicit approval and
retain encryptedEBS (disk charges continue). Terminate/root-volume deletion only
with separate explicit data-disposal approval. Cleanup this root's worker/SG/rules
only; review destroy plan for17ownedresources and no production instance. Remove
only the named worker Node object/credentials under separate cluster approval.
Do not drain or delete server Node, Voting namespace,PostgreSQLPVC or sharedCRDs.

## Validated locally

Terraformfmt/validatePASS; init reused the previously verified provider package
and lockfile from the production working directory (mirror reported unauthenticated
installation metadata; no new signature verification claimed). Saved liveplan
PASS17create0update0destroy. Independent JSON review confirms every actioncreate
and no existing instance resource. Cloud-init is configuration only, not executed.
No infrastructure, join, bootstrap or destroy/recreate demonstration is claimed.

References: [K3sprivateports](https://docs.k3s.io/installation/requirements),
[AWScredits](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/useconsolidatedbilling-credits.html),
[IPv4pricing](https://aws.amazon.com/vpc/pricing/),
[PriceListAPI](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/price-changes.html).

## Optional genuine disposable Terraform lifecycle demonstration

After separate approval to create the worker, but BEFORE agent join/token supply
or any workload/PVC, the empty worker state can support a separately approved
destroy/recreate demonstration. Capture private state resource IDs and the initial
apply receipt; prepare a destroy plan from terraform-worker only; require exactly
the17ownedworker/rule resources and no server instance, volume, subnet or IAMrole.
Obtain explicit destruction approval, apply only that reviewed saved plan, then
prepare/review a new create plan and obtain recreate approval. Verify new worker
instance ID, SSM/bootstrap and identical declared settings before joining. No
existing production data or database may be part of this test. Budget20–40minutes
plus bootstrap and a small additional prorated compute/IP/disk charge within the
reviewed allowance; no capacity guarantee. Never perform this after RobotShop
data exists without separate retention/disposal approval. This would demonstrate
the disposable worker extension lifecycle, not full production infrastructure
recreation or PostgreSQL recovery. No destroy/recreate has been executed here.

Additional workload gate: the four focus RobotShop adapters and load generator are presently local images, not published AWS-pullable release artifacts. Before AWS deployment, separately approve registry publication/artifact transfer, verify exact immutable identities and complete fresh scanning or explicitly review the unresolved scan risk. No image publishing or new registry credentials were authorized by this worker proposal. The existingVotingGHCRimages are a separate release.

Additionalofflinechecks: cloud-initYAML parses, root-owned0700bootstrap/no-token-file contract passes, extracted bootstrapShellCheck0.11passes with binaryLFstdin; check_plan.py independently validates17create-only actions, privateingress ports, encrypted50GiBdisk, IMDSv2 and noautomaticjoin. The first Windows text-mode stdin check introducedCRLF; binaryinput correctedthetesttransport withoutchangingthetemplateor savedplan.
