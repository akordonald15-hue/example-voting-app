# Requirement-to-evidence index

## Capstone 1

| Requirement | Proof / review entry | Evidence boundary |
|---|---|---|
| Compose and hardening | [Recorded extracts](evidence/capstone1-local-reports.md);[Vote Dockerfile](../vote/Dockerfile);[Result](../result/Dockerfile);[Worker](../worker/Dockerfile) | Recorded local report/source, not fresh runtime screenshots |
| Infrastructure | [Terraform](../terraform/);[worker root](../terraform-worker/);[sanitized scope](evidence/infrastructure-status.json) | Prior execution plus owner confirmation; no destroy/recreate |
| AWS application/health | [Scope and missing raw evidence](evidence/infrastructure-status.json);[Helm source](../helm/voting-app/README.md) | Owner-confirmed healthy checkpoint; no fresh live calls |
| Hosted CI/security | [Run40294083665attempt2](https://github.com/akordonald15-hue/example-voting-app/actions/runs/40294083665/attempts/2);[workflow](../.github/workflows/capstone.yaml) | Hosted artifacts/access/retention must be checked before submission; not downloaded during closeout |
| Published images | [Recorded release refs](evidence/capstone1-published-images.json) | Not proof those exact images run in production |
| Rollback | [Exact local fixture and receipts](../docs/rollback-evidence/README.md);[final history](../docs/rollback-evidence/final-helm-history.txt);[final Pod status](../docs/rollback-evidence/final-pod-status.txt) | Local Vote fixture, not production or full application |
| Architecture/reproduction | [Diagrams](architecture.md);[instructions](reproduction.md) | Configured versus demonstrated flows labelled |

## Capstone 2

| Requirement | Retained proof | Boundary |
|---|---|---|
| Provenance/services | [Upstream receipt](../capstone2/upstream-receipt.json);[Pod checkpoint](../capstone2/evidence/runtime/robot-shop-latest.json);[build evidence](../capstone2/instrumentation/build-evidence.md) | Local kind |
| Checkout | [11-step flow](../capstone2/evidence/runtime/shopping-flow.json) | Simulated payment |
| Failed initial load | [65/70summary](../capstone2/evidence/runtime/load-summary.json);[Job status](../capstone2/evidence/runtime/loadgen-verified-status.json) |5 failures;unsuccessfulJob |
| Failed bulk-city load | [124/126summary](../capstone2/evidence/runtime/load-e2e-summary.json);[Job status](../capstone2/evidence/runtime/loadgen-e2e-status.json) |2 failures;JobFailed |
| Browser profile | [151/151summary](../capstone2/evidence/runtime/loadgen-browser-summary.json);[Job outcome](../capstone2/evidence/runtime/loadgen-browser-job-result.json);[traffic disclosure](../capstone2/evidence/runtime/shipping-reliability.md) |1user3m;8 simulated orders;not bulk-city fix |
| RED/dashboard | [Exported JSON](../capstone2/evidence/dashboard/robot-shop-exported.json);[Grafana panel responses](../capstone2/evidence/dashboard/grafana-panels-20261026T2056Z.json);[interpretation](../capstone2/evidence/dashboard/README.md) | Real query data;no screenshot |
| Logs | [Loki query](../capstone2/evidence/runtime/loki-web-info-query.json);[labels](../capstone2/evidence/runtime/loki-labels.json) | Selected Web logs |
| Traces | [Catalogue spans](../capstone2/evidence/runtime/jaeger-v3-catalogue-traces.ndjson);[services](../capstone2/evidence/runtime/jaeger-v3-services.json) | Not complete checkout trace |
| SLO/alerts | [Policy](../capstone2/SLO.md);[runbook](../capstone2/runbook.md);[rules](../capstone2/observability/config/rules.yaml) | Below target snapshot;Slack not delivered |
| Incident | [Timeline](../capstone2/evidence/runtime/incident-timeline.json);[firing](../capstone2/evidence/runtime/incident-sample-3.json);[recovery](../capstone2/evidence/runtime/incident-recovery.json);[resolved](../capstone2/evidence/runtime/incident-alerts-followup.json);[postmortem](incidents.md) | Local controlled drill, not AWS |
| Security limitation | [Trivy status](../capstone2/evidence/security/README.md);[bounded retry](../capstone2/evidence/security/bounded-retry.json) | Incomplete scan, not zero findings |
| AWS worker/isolation | [Scope receipt](evidence/infrastructure-status.json);[worker source](../terraform-worker/) | Owner-confirmed join;raw status evidence missing |
| AWS overlays | [App](../capstone2/aws/robot-shop.values.yaml);[monitoring](../capstone2/aws/monitoring.values.yaml);[aux](../capstone2/aws/observability.values.yaml);[audit](../capstone2/aws/review/render-audit.json);[CRD/RBAC inventory](../capstone2/aws/review/cluster-scoped.json) | Offline structural checks;not AWS success |
| GHCR/DNS | [Sanitized final snapshot](evidence/capstone2-publication.json);[verified public registry metadata](../capstone2/aws/phase2a/registry-verification.json);[image inventory](../capstone2/aws/phase2a/complete-inventory.json) | Web/Cart only;no more publication |

## Screenshots and missing attachments

No new browser/console/dashboard screenshots were captured. Product artwork and architecture images are not runtime screenshots. Existing JSON, logs, Helm history and traces are the authentic evidence. Owner production-browser screenshots, raw sanitized current Helm/node/PVC status and worker-join output remain missing from this public package. Submit only genuine owner-supplied attachments after redaction; never generate success screenshots.

Retained local load logs: [browser-profile successful run](../capstone2/evidence/runtime/loadgen-browser-3m.log),[failed bulk-city run](../capstone2/evidence/runtime/loadgen-e2e.log). These are genuine local artifacts, not new runs or screenshots.
