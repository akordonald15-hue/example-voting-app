# Capstone K3s infrastructure — local preparation only

**Current checkpoint — 2026-10-25:** EC2/K3s is deployed and the owner reports healthy Helm revision 2. The original preparation narrative below is historical. Terraform recreation has not been demonstrated; preserve the recovered database and follow the [current completion/recreation runbook](../docs/capstone-completion.md). No apply/destroy is authorized by this README.

No infrastructure has been provisioned. Do not run a plan, apply, or destroy until separately authorized. Run all future Terraform commands from this directory or with `-chdir=terraform` from the repository root. Read `docs/phase-5-terraform-plan.md` for discovery, pricing and limitations.

## Design

- Fixed region eu-west-1 and named AWS profile capstone; no credentials in code.
- Data-only references to the existing default VPC and explicitly selected default subnet (eu-west-1a).
- One Ubuntu 24.04 amd64 EC2 node, initially t3.medium / 30 GiB encrypted gp3, IMDSv2 required, T3 standard CPU-credit mode.
- Dedicated security group: **no inbound rules**, including no SSH, public Kubernetes API or NodePorts. Outbound TCP 443/80 for SSM, registry/release downloads, Snap and Ubuntu bootstrap; VPC DNS and Amazon Time Sync rules. Security groups cannot filter DNS/IMDS link-local traffic in every case; these rules are not a host firewall.
- An EC2 role/profile with AmazonSSMManagedInstanceCore only. This role is for the node; it does not grant the operator provisioning or Session Manager permissions.
- Pinned K3s v1.36.5+k3s1 binary and verified amd64 SHA-256 in cloud-init; Ubuntu apt and SSM agent updates are not fully frozen.
- Local state only; .terraform, state, private variables, plans and kubeconfigs ignored. Provider checksums in .terraform.lock.hcl remain eligible for later authorized version control.

`approve_public_egress=false` prevents a usable future provisioning plan until explicitly approved. It is a review guard, not a substitute for authorization. The proposed public IPv4 supplies outbound connectivity through the existing Internet gateway; it does not open ingress. NAT and paid interface endpoints are not included. Public-egress approval remains outstanding.

AMI `ami-03c066fbf8c68378e` was verified as available Canonical Ubuntu 24.04 amd64 in eu-west-1 on 19 October 2026. K3s 1.36 aligns with installed kubectl 1.36.1; cloud bootstrap is not yet tested. No SSH key is created or required.

## Local checks

Recovery result (19 October 2026): official hashicorp/aws 6.69.1 archive was downloaded with resumable TLS-verified IPv4, matched against official signed checksums using HashiCorp's current public key, and installed from a temporary local mirror. An ordinary subsequent `terraform init -backend=false -input=false -lockfile=readonly` succeeded using the installed provider. fmt -check and validate both passed. No resource configuration changed. The lockfile currently covers Windows amd64 only; obtain official Linux hashes before later Linux CI use. See the Phase 5 report for the stale-key warning and its resolution. No TLS/signature checks were disabled.

Only formatting, provider initialization without backend, and validation are authorized now:

```powershell
terraform fmt -recursive
terraform init -backend=false -input=false
terraform fmt -check -recursive
terraform validate
```

These do not prove AWS permissions, quota availability at launch, instance capacity, bootstrap success or cluster readiness. The current ReadOnlyAccess identity cannot provision or start SSM sessions. No execution plan has been run.

## Future deployment procedure — do not execute yet

The administrator's scoped permission review should cover EC2 launch/termination and tagging, instance attribute updates for reviewed resizing, dedicated security-group creation/deletion and egress authorization/revocation, instance-profile association as needed, plus IAM role/profile creation/deletion, adding/removing the role from its profile, and attaching/detaching only AmazonSSMManagedInstanceCore. Restrict iam:PassRole to the project EC2 role and ec2.amazonaws.com. Use project tags/name prefixes and approved subnet/AMI/region conditions where the action supports them. Keep read-only discovery separate. Session Manager operator access needs StartSession on project nodes and approved shell/port-forward documents, and own-session ResumeSession/TerminateSession plus session data-channel access. Exact effective permissions must be reviewed by the administrator; do not add AdministratorAccess or change ReadOnlyAccess automatically. Account policies/SCPs may impose further restrictions.

1. Obtain explicit architecture/spend/public-egress approval and administrator-reviewed scoped Terraform and SSM permissions. Reconfirm credit expiration/product coverage and the default subnet route. Install Helm and the Session Manager plugin only with approval.
2. Create a local terraform.tfvars from the safe example. Change approve_public_egress only after approval. Keep credentials in the named AWS profile, never in tfvars. Select disk/data deletion policy before provisioning: the code deletes the EC2 root volume on termination.
3. After authorization to plan, run `terraform plan -out=review.tfplan`; review every action. Only project EC2, disk, security group/rules, role/profile/attachment should be created. No shared networking may be modified. Securely inspect the plan without publishing it.
4. Obtain explicit approval of that concrete plan before `terraform apply review.tfplan`. A saved plan becomes stale when code, inputs or infrastructure changes; re-plan and re-review then. No plan/apply has been performed during preparation.
5. Check the instance is managed by SSM. In a Console Session Manager terminal, inspect `cloud-init status --wait`, `systemctl status k3s`, `/var/lib/capstone-k3s-ready` and `sudo /usr/local/bin/k3s kubectl get nodes -o wide`. Check system pods, disk and memory; EC2 running alone is insufficient. Investigate failures via cloud-init/systemd logs without publishing credentials.
6. Start the tunnel from a separate local terminal using the safe Terraform output command (Session Manager plugin required):

```powershell
aws ssm start-session --target <instance-id> --document-name AWS-StartPortForwardingSession --parameters portNumber=6443,localPortNumber=16443 --profile capstone --region eu-west-1
```

7. Obtain `/etc/rancher/k3s/k3s.yaml` privately through your own authorized Session Manager terminal and save it outside Git with user-only Windows ACLs. It contains an administrative private key: never send its contents to chat/tools/logs or Terraform outputs. Change only its server endpoint to `https://127.0.0.1:16443`; preserve CA/client certificates. Do not disable TLS verification. Use `kubectl --kubeconfig <private-path> get nodes` and later `helm --kubeconfig <private-path> ...` with the tunnel open. Avoid changing an unrelated default kubeconfig/context.
8. In the later authorized CI/Helm phase, publish hardened final images to GHCR by immutable application digest, deploy five workloads with one chart/values file, and use PostgreSQL PVCs, probes and security/resource settings. Existing sample emptyDir manifests are not production-ready. Port-forward vote/results to 18080/18081 to preserve the local Compose app's ports.

## Public access and cost boundary

The present configuration supports private administration and local browser testing through Session Manager plus kubectl port-forward. It deliberately does **not** publish an Internet-accessible Voting App URL. The public IPv4 is for egress only; zero inbound rules block direct public NodePort/HTTP/API access. Traefik and ServiceLB are disabled. A later public release requires an approved ingress/controller, TLS/certificate and DNS plan, associated security-group changes and updated costs. Do not open the Kubernetes API or databases as a shortcut. A direct-node ingress could use the existing IP but adds operational/TLS work; a managed load balancer adds hourly/capacity/IP charges. Neither is implemented here.

No NAT Gateway or interface VPC endpoints are included, so this design has no NAT hourly/per-GB processing charge. The existing Internet gateway is not a managed NAT Gateway. EC2 compute, one public IPv4, gp3 disk, transfer and any later snapshots are still billable. SSM port-forwarding traffic can contribute to transfer usage. Credits and shared transfer allowances are not guaranteed to cover them.

## Permission review checklist (no grants performed)

Alongside existing read-only lookups, review initial creation/deletion permissions for `ec2:RunInstances`, `ec2:TerminateInstances`, `ec2:CreateTags`, `ec2:DeleteTags`, `ec2:CreateSecurityGroup`, `ec2:DeleteSecurityGroup`, `ec2:AuthorizeSecurityGroupEgress`, `ec2:RevokeSecurityGroupEgress`, `iam:CreateRole`, `iam:DeleteRole`, `iam:AttachRolePolicy`, `iam:DetachRolePolicy`, `iam:CreateInstanceProfile`, `iam:DeleteInstanceProfile`, `iam:AddRoleToInstanceProfile`, `iam:RemoveRoleFromInstanceProfile`, IAM role/profile tagging, and tightly scoped `iam:PassRole`. RunInstances needs authorization for the selected AMI, subnet, security group, network interface, volume and instance resources as applicable, not just the instance ARN. No inbound-rule permission is needed for the current zero-ingress design.

Limit IAM policy attachments to AmazonSSMManagedInstanceCore and PassRole to the project node role with `iam:PassedToService=ec2.amazonaws.com`. Scope region, project tags/name prefixes and pre-existing subnet/AMI wherever supported. Do not permit privilege escalation through unrestricted role creation, attachment or PassRole. Future resizing/updates may additionally need StopInstances/StartInstances/ModifyInstanceAttribute, ModifyInstanceMetadataOptions, ModifyVolume, or instance-profile association changes; review the concrete future plan before granting these. Session Manager operator actions are separate from both Terraform and the node role. A policy simulation is not a substitute for account-administrator review of conditions, permissions boundaries and SCPs.

## Downloaded credential JSON

Only existence/path/metadata checks were performed. `C:\Users\akord\Downloads\capstone-key.json` is outside the repository, and configured CLI authentication as devops-capstone was reverified. The downloaded export is no longer needed for ordinary AWS CLI use once the profile works. It has not been deleted; explicit deletion approval is required. Ordinary deletion removes that copy but does not guarantee forensic erasure on SSDs/backups or revoke the access key. The configured local AWS profile still contains credentials; keep it protected. Do not change/revoke credentials as part of provider recovery without separate authorization.

## Sizing and lifecycle

Start with t3.medium only for the Voting App. Capstone 2 needs a separate capacity exercise; t3.xlarge (4 vCPU/16 GiB, standard CPU credits) is a cost-oriented trial, while m6i.xlarge avoids sustained CPU credit throttling. Neither has been workload-tested. Measure actual requests/limits, headroom and metrics/log retention before selecting; do not assume 4 or 8 GiB supports Robot Shop plus observability. Current regional standard On-Demand quota is 5 vCPUs; overlapping a 2-vCPU old node and 4-vCPU replacement would exceed it. Do not use create-before-destroy blindly.

Instance resizing can stop/restart the node and causes total cluster downtime. Disk growth cannot be reversed by reducing a Terraform variable. Changing user-data deliberately replaces this disposable node; review data impact first. Recheck pinned version availability and security before a delayed deployment.

Destroying this instance deletes its root EBS volume and all K3s/local-path application data. Cluster recreation is not data restoration. Preserve/backup any required cloud PostgreSQL data first. Local Docker's database volume is unrelated and must remain untouched.

Before a later destroy, obtain explicit approval for the exact resource/data-loss scope, uninstall approved Helm resources, back up needed data, and inspect `terraform plan -destroy -out=destroy.tfplan`. Execute `terraform apply destroy.tfplan` only after approval. Preserve Terraform state. Verify all project-tagged instances, disks, security groups, IAM profiles/roles and any separately created snapshots, IPs or load balancers; do not remove shared default VPC/subnets/routes. Billing data can lag.

Recreate from the same reviewed code, lockfile and safe inputs after renewed approval. Expect a new instance ID; repeat SSM/bootstrap/node verification, obtain the new kubeconfig privately, restore approved backups or explicitly begin with fresh cloud data, and repeat voting verification in the later Helm phase. An empty/drift-free plan must be explicitly authorized too. No destroy/recreate or cloud deployment is executed by this README.
