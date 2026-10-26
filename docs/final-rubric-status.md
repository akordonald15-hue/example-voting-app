# Final submission rubric status — October26,2026

This is an evidence inventory, not an assertion of instructor grading. Only items
actually demonstrated are marked verified. Local and AWS results are distinct.

| Capstone1 requirement | Status and scope | Evidence |
|---|---|---|
| Compose application and image hardening | Previously verified locally | Main README and submission-readiness.md |
| Terraform AWS provisioning | Previously performed; existing K3s production retained | Terraform source and owner deployment evidence |
| Hosted CI acceptance/security/GHCR | Previously verified hosted:13guards,9acceptance checks,3all-severity scans; published immutable digests | submission-readiness.md links hosted run |
| Helm application on AWS | Owner-confirmed revision2 deployed; five healthy workloads; protected PostgreSQL PVC | Owner evidence, historical stage5 notes |
| Helm rollback | Verified isolated local Vote-only fixture | rollback-evidence/; not production/full-stack rollback |
| Automated CI production deployment | Not demonstrated; deployment opt-in disabled | Workflow and documented limitations |
| Terraform destroy/recreate | Not demonstrated | Do not imply source-only reproducibility proves execution |
| Submission documentation/architecture | Prepared locally | Main README and submission-readiness.md |

| Capstone2 requirement | Status and scope | Evidence |
|---|---|---|
| Robot Shop services and stores | All12Pods observed Ready in local kind, not AWS | ../capstone2/evidence/runtime/robot-shop-latest.json |
| Instana removal | Four focus adapters built without active Instana; legacy supporting images remain pinned upstream | Build receipts and source |
| Prometheus RED | Real exported/scraped series; assess each panel independently | Runtime and dashboard query receipts |
| Grafana | Ready/healthy; seven-panel dashboard exported and real queries captured; Payment series absent | ../capstone2/evidence/dashboard/ |
| Fluent Bit/Loki | Real Web service/level log search verified | loki-web-info-query.json |
| OTEL/Jaeger | Catalogue HTTP spans retrieved | jaeger-v3-catalogue-traces.ndjson |
| Load/shopping flow | Registration direct/proxy200; bounded run70requests/5failures; Shipping prevents checkout | registration-direct-proxy.json and load receipts |
| SLO/error budget | Policy/rules prepared; no99%attainment claim from short rehearsal | SLO.md and measured panel result |
| Actionable Slack alert | Rule/runbook prepared; no delivered notification verified | Missing webhook/workspace access; local-no-delivery receiver |
| Incident/postmortem | Local catalogue-loss: firing alert, restoration, probe1 and subsequent alert resolution | postmortem-local.md and incident receipts |
| Fresh complete Trivy scan | Blocked by memory; findings unknown, not zero | ../capstone2/evidence/security/ |
| Shared AWS scenario/own Robot Shop fork | Not demonstrated | Local namespace-isolated rehearsal in Voting repository |

## Submission procedure

Review the main README, Capstone1 submission-readiness.md and Capstone2 SUBMISSION.md.
Use genuine receipts and label owner-provided AWS evidence explicitly. Request
approval for uploading the reviewed feature branch; no local-only commit link is
represented as available on GitHub. Submit the approved commit URL and these
indexes after upload. Disclose incomplete Slack, scanning and scenario deviations.
Never upload kubeconfigs, tokens, webhooks, Terraform state/variable secrets,
private promotion bundles, raw User logs or user database exports.

Current branch is feature/capstone1-ci-release-readiness. Expected origin is
https://github.com/akordonald15-hue/example-voting-app.git. No main merge, AWS
modification, production deployment or infrastructure action is part of closeout.
