# Voting App AWS infrastructure source

[Current submission scope and evidence](../submission/capstone1.md). This root describes the existing Voting App K3s server. Infrastructure provisioning was previously performed; this closeout did not execute Terraform/AWS commands. Live application health is owner-confirmed at the accepted checkpoint.

Review main.tf, variables.tf, outputs.tf, cloud-init template and safe example inputs in this directory. Real terraform.tfvars, state, saved plans, credentials and apply logs are private/excluded. Source reproducibility is NOT a demonstrated destroy/recreate test; destroy/recreate remains incomplete.

The production PostgreSQL local-path claim is bound to its node. Instance/root-volume deletion or replacement may destroy its data. Never apply, destroy, resize, replace or recover infrastructure as part of submission review. A future lifecycle operation requires separate exact-plan/spend/data-safety approval.

[Architecture](../submission/architecture.md) · [limitations](../submission/requirement-matrix.md) · [safe reproduction boundaries](../submission/reproduction.md).
