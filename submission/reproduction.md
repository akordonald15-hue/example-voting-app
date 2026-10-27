# Reproduction and troubleshooting

These are instructions for a future approved disposable environment, not newly executed tests. First inspect the selected Docker/kube context and avoid the AWS production cluster. Do not run lifecycle/cleanup commands against the working Voting App or delete volumes.

## Voting App

Review [Compose](../docker-compose.yml), Dockerfile final targets and [Helm chart](../helm/voting-app/README.md). In an isolated local workspace/project with free ports, the upstream local entry point is `docker compose up --build`. Browser Vote8080/Result8081. Existing healthy local containers need not be restarted to review retained evidence. [Historical local extract](evidence/capstone1-local-reports.md).

[Terraform](../terraform/) and [worker Terraform](../terraform-worker/) contain source/example inputs; credentials, state, real inputs and plans are excluded. Never run apply/destroy from submission instructions without exact separate approval. No destroy/recreate demonstration is included.

Review [.github/workflows/capstone.yaml](../.github/workflows/capstone.yaml) and hosted run. Independent publish/deploy opt-ins must stay disabled unless separately approved. No runner registration or production deployment is part of reproduction here.

For the isolated Vote-only rollback, follow the exact [fixture/evidence](../docs/rollback-evidence/README.md) in a disposable local cluster. Do not rerun it against capstone/voting-app or PostgreSQL.

## Robot Shop

Review [local values](../capstone2/local-demo.values.yaml), [chart](../capstone2/robot-shop/), [monitoring local values](../capstone2/monitoring-local.values.yaml), [auxiliary local values](../capstone2/auxiliary-local.values.yaml), [build contexts](../capstone2/instrumentation/build-evidence.md). Local images must be built/loaded into kind first; local tags are not remotely pullable. Image dependencies and actual tested IDs are recorded in [inventory](../capstone2/aws/phase2a/complete-inventory.json). Default immutable-image gates intentionally prevent deployment when pins are missing.

Future isolated local installation sequence is Robot Shop, then kube-prometheus-stack92.7.0, then auxiliary chart. Namespace robot-shop/observability only. No runnable install command is requested during this closeout. [AWS values](../capstone2/aws/robot-shop.values.yaml) are NOT local kind values: they target the tainted worker and remain incomplete. Do not deploy them.

Safe offline review, after supplying existing local Helm/chart paths:

```powershell
python capstone2/aws/audit.py --helm '<HELM_EXE>' --monitoring-chart '<kube-prometheus-stack-92.7.0.tgz>'
```

The package SHA is checked by the script. Empty image refs use clearly labelled structural fixtures; audit PASS is not deployment GO. Do not add --require-real-images until every pin is populated; that mode must reject the current incomplete set. No package download, Helm install or live cluster access is implied.

Shipping/Cart troubleshooting: exact service DNS/ports and bounded CPU were corrected locally. Bulk city-list routes still timed out; browser autocomplete profile changed traffic shape and succeeded. [Evidence](../capstone2/evidence/runtime/shipping-reliability.md). Do not hide original failed Jobs.

GHCR troubleshooting: Web/Cart verified; Catalogue registry PUT failed with `lookup ghcr.io: no such host`. Windows/Docker stability samples were intermittent; no DNS/proxy/reset changes were made. Keep publication stopped. Fresh Trivy scans are blocked by memory; do not stop databases/brokers/kind or claim zero findings.

## Evidence export

Use existing sanitized JSON/logs instead of rerunning infrastructure operations. Do not export Kubernetes Secret data, kubeconfig, database records, GitHub tokens or Slack webhook URLs. Keep provider console screenshots private until redacted for account IDs, addresses and credentials. Screenshot absence is disclosed, not filled with generated images.
