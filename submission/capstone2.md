# Capstone 2 — Robot Shop observability

**Submission summary:** A12-service/store Robot Shop rehearsal in local kind with simulated checkout, bounded browser-profile load, four-service RED queries through Grafana, Loki log search, retrieved Catalogue traces and a controlled local catalogue-loss incident. This is **not an AWS Robot Shop deployment**.

## Application and load evidence

[Adapted upstream Helm chart](../capstone2/robot-shop/), [upstream provenance](../capstone2/upstream-receipt.json), [instrumented build evidence](../capstone2/instrumentation/build-evidence.md), [local Pod checkpoint](../capstone2/evidence/runtime/robot-shop-latest.json). Focus adapters remove active Instana usage; do not imply every legacy upstream supporting image was rebuilt/hardened.

[Simulated checkout](../capstone2/evidence/runtime/shopping-flow.json):11 HTTP 200 steps and a simulated order, not a real payment gateway transaction.

| Bounded local load | Result | Disclosure |
|---|---|---|
| Initial run |65/70 successes;5 failures;92.8571%success | Locust exit1; Job unsuccessful/DeadlineExceeded; cart/add1 and shipping/codes4 failures. [Receipt](../capstone2/evidence/runtime/load-summary.json) |
| Later original bulk-city profile |124/126 successes;2 failures;98.41%success | Shipping city-list timeouts; Locust exit1; JobFailed. [Receipt](../capstone2/evidence/runtime/load-e2e-summary.json) |
| Browser-equivalent autocomplete profile |151/151 successes;0 failures;8 simulated orders |1 user / 3 minutes;193 s Job elapsed; succeeded/exit0. Different profile, not proof the bulk-city endpoint was fixed. [Receipt](../capstone2/evidence/runtime/loadgen-browser-summary.json) |

## Observability evidence

- [Grafana exported dashboard](../capstone2/evidence/dashboard/robot-shop-exported.json), [authenticated final panel queries](../capstone2/evidence/dashboard/grafana-panels-20261026T2056Z.json), [capture interpretation](../capstone2/evidence/dashboard/README.md): real Web/Catalogue/Cart/Payment request/rate/p95 data. Earlier startup/unready failures retained. No browser dashboard screenshot exists.
- [Loki Web log query](../capstone2/evidence/runtime/loki-web-info-query.json): actual service/level labels. Not proof every service was queried.
- [Retrieved Catalogue Jaeger spans](../capstone2/evidence/runtime/jaeger-v3-catalogue-traces.ndjson): actual HTTP traces; not a complete checkout trace.
- [SLO and budget policy](../capstone2/SLO.md):99% synthetic catalogue-path availability over1h. Last dashboard snapshot ~96.667%, below target with negative budget. Full-hour attainment was not demonstrated; missing data is not success.
- [Alert/runbook](../capstone2/runbook.md) and rule configuration exist. The local receiver sends no notifications; **Slack delivery not demonstrated**, no approved webhook provisioned.
- [Local postmortem](../capstone2/postmortem-local.md), [incident summary](incidents.md): catalogue loss caused alert pending/firing; replica restored; probe recovered; later active alerts empty. Not an AWS incident and not evidence Slack was delivered.

## AWS preparation and publication

Owner confirms a Ready isolated worker with4 CPU / ~15.3GiB, dedicated label/NoSchedule taint; Voting App stayed on the server. Terraform worker apply recorded17 additions/0 changes/0 deletions. Join/TLS/DNS/kubelet/protection evidence is owner-confirmed, not raw output captured by this closeout. [Scope receipt](evidence/infrastructure-status.json).

[AWS Robot Shop values](../capstone2/aws/robot-shop.values.yaml), [monitoring values](../capstone2/aws/monitoring.values.yaml), [auxiliary values](../capstone2/aws/observability.values.yaml), [offline audit](../capstone2/aws/review/render-audit.json), [cluster-scoped inventory](../capstone2/aws/review/cluster-scoped.json): templates reviewed for worker-only placement/private Services/resources. Current audit is structural:3 custom pins remain empty and are represented only by labelled fixtures during rendering. No deployability claim.

[Publication snapshot](evidence/capstone2-publication.json): Web/Cart published and config/amd64 verified; Catalogue push failed once with DNS lookup failure and partial artifacts remain; Payment/Browser Loadgen not pushed. Subsequent read-only stability test failed intermittently on Windows and Docker. No publication retry or deployment is authorized now.

## Incomplete

Robot Shop same-cluster AWS scenario,3 remaining image publications, private Kubernetes pulls, Grafana credentials, live storage/CRD/RBAC checks, Slack delivery and fresh full Trivy scans remain incomplete. [Trivy failure/restoration receipts](../capstone2/evidence/security/README.md): database extraction failed for memory; bounded retry failed; vulnerability counts unknown. Do not substitute npm audit for full image scanning.

No own Robot Shop fork or instructor-specific starter/drill evidence is claimed. Current work is in the Voting App repository, based on instana/robot-shop. [Reproduction and safety](reproduction.md), [architecture](architecture.md), [complete matrix](requirement-matrix.md).
