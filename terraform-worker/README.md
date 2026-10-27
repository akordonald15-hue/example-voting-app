# Separate K3s worker infrastructure root

[Current submission scope](../submission/capstone2.md). This root isolates the later worker from the Voting App server state. Recorded infrastructure apply:17 additions,0 modifications,0 deletions;private security-group additions included server-attached rules, so zero Terraform updates does not mean production networking was unchanged. Raw plans/state/IAM policy/account identifiers remain private.

Owner subsequently confirmed worker join/version/TLS/DNS/kubelet and production protection checks. Worker4 CPU / ~15.3GiB, capstone-workload=robot-shop label and matching NoSchedule taint. Robot Shop was NOT deployed to AWS. [Evidence boundary](../submission/evidence/infrastructure-status.json).

Code includes encrypted50 GiB gp3 and reviewed m7i.xlarge with private K3s traffic. Existing approved gross allowance was10 USD / 24 hours; cleanup-deadline tag is not an automatic shutdown mechanism. No stop/delete/extension action is authorized by this README. Charges continue until an approved lifecycle action; confirm disposition with the owner separately.

Source does not grant permission to apply/join/deploy. Keep actual inputs, join token, state, plan and administrator IAM bundle outside Git. No Terraform destroy/recreate demonstration is claimed. Do not remove production databases/claims or drain the server.
