# Completed versus incomplete requirements

These are evidence assessments, not instructor grades. Recorded results are historical; no live service checks were rerun for packaging.

| Project / requirement | Status | Scope or gap |
|---|---|---|
| C1 Compose execution | COMPLETE — recorded | Local browser/vote flow and historical report extract |
| C1 Docker hardening | COMPLETE — recorded/source | Final-target/non-root configuration; no new scan |
| C1 Terraform provisioning | COMPLETE — recorded/owner | Existing server plus separate worker; raw private state/logs excluded |
| C1 Terraform destroy/recreate | INCOMPLETE | Never demonstrated |
| C1 AWS Helm application | COMPLETE — owner-confirmed checkpoint | Revision2, healthy five workloads, PostgreSQL preserved; fresh public screenshots missing |
| C1 Hosted tests/Trivy/GHCR | COMPLETE — recorded run |13 guards,9 acceptance,3 all-severity scans; historical result only |
| C1 Automatic production deploy | INCOMPLETE | Successful run skipped deploy; private runner/promotion prerequisites not activated |
| C1 Helm rollback | PARTIAL rubric scope | Isolated local Vote-only fixture passed; no full-stack/AWS rollback/database restore |
| C2 Instana removal/adaptation | PARTIAL | Four focus adapters; pinned legacy support images remain |
| C2 Local Kubernetes services/stores | COMPLETE — local |12 workloads recorded Ready; not AWS |
| C2 Simulated checkout | COMPLETE — local |11 HTTP 200 steps; simulated gateway, not real payment |
| C2 Sustained load | PARTIAL / profile-specific |65/70 and 124/126failed Jobs retained; separate1-user3m browser profile151/151passed |
| C2 Prometheus/Grafana RED | COMPLETE — local query evidence | Four focus services; provisioned/exported dashboard; browser screenshot absent |
| C2 Fluent Bit/Loki | COMPLETE — demonstrated subset | Web service/level log query; not every service validated |
| C2 OTEL/Jaeger | COMPLETE — demonstrated subset | Catalogue HTTP spans retrieved; not full checkout trace |
| C2 SLO/error budget | COMPLETE policy; attainment INCOMPLETE |99% / 1 h synthetic-path policy; measured snapshot below target |
| C2 Slack alert | PARTIAL | Alert evaluation/rule/runbook present; delivery not demonstrated, no webhook |
| C2 Incident/postmortem | COMPLETE — local only | Catalogue loss, firing, restore, probe recovery, alert resolution; no AWS incident |
| C2 Fresh complete Trivy | INCOMPLETE | Memory/database extraction failure; findings unknown |
| C2 AWS worker | COMPLETE infra; owner-confirmed join |4 CPU / ~15.3GiB, dedicated label/taint; not Robot Shop AWS deployment |
| C2 AWS overlays/offline checks | COMPLETE preparation only | Structural fixtures for3missing images; cluster-scoped risks retained |
| C2 GHCR images | PARTIAL | Web/Cart verified; Catalogue DNS failure; Payment/Loadgen not pushed |
| C2 Same AWS cluster deployment | INCOMPLETE | Robot Shop never deployed to AWS |
| C2 Separate Robot Shop fork/instructor starter scenario | DEVIATION | Based on upstream snapshot within Voting App repository; independent local drill |
| Submission upload/access | PENDING approval | New guides/receipts are local; no commit/push in this closeout |

[Exact evidence links](evidence-index.md) · [Missing evidence and submission checklist](git-and-submission.md)
