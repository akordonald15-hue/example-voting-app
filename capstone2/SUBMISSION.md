# Robot Shop submission evidence index

Checkpoint: October 26, 2026. Deadline: October 27, 12:00 WAT.

| Requirement | Actual checkpoint | Evidence |
|---|---|---|
| Pinned source/chart | Prepared from upstream `55292e2199f2fb00a165b1f7d3045fe7f8922038` | [Receipt](upstream-receipt.json), [chart](robot-shop/) |
| Four focus builds without active Instana | Web, Catalogue, Cart, Payment local builds completed | [Cart/Catalogue](instrumentation/build-evidence.md), [Web](local-services/web/), [Payment](local-services/payment/) |
| RED instrumentation | Real counter/histogram export passed isolated tests | [Middleware tests](instrumentation/test-red.cjs), [Web smoke](local-services/web/smoke.cjs), [Payment smoke](local-services/payment/smoke.py) |
| Trace instrumentation | Cart/Catalogue request trace IDs observed; Payment actual OTLP protobuf POST captured locally | Build receipts and Payment smoke; not yet a retrieved Jaeger trace |
| Application deployment | Local kind installation underway; no all-Ready/checkout claim yet | Add genuine runtime receipts after verification |
| Steady upstream load | Build assets prepared, sustained result pending | [Local load generator](local-services/loadgen/) |
| Prometheus/Grafana | Official chart92.7.0 and values prepared; integrated query/dashboard proof pending | [Local values](monitoring-local.values.yaml) |
| Fluent Bit/Loki | Service/level configuration prepared; real query pending | [Configs](observability/config/) |
| Jaeger | Collector/backend configured; retrieved request trace pending | [Auxiliary chart](observability/) |
| SLO/error budget | Written policy prepared, sustained measurement pending | [SLO](SLO.md) |
| Slack | Rule/runbook prepared; actual firing/resolved delivery not demonstrated | [Runbook](runbook.md) |
| Incident/postmortem | No incident result claimed | Record actual timeline, mitigation and recovery before finalizing |

## Local image evidence

Web tests verified static page200, health200, missing-path404 counter and latency
histogram; browser controller syntax checked with Node. Payment tests verified
health200, full metric registry, item-count logic and actual OTLP `/v1/traces`
payload receipt. Tests used disposable containers, no network, read-only root
filesystem and all Linux capabilities dropped. They are not a complete checkout.

Web local ID:
`sha256:9ded3c31ca93f19ecdc3aedc555ac73bf8347542df04e47460605963efeecf3d`.

Payment local ID:
`sha256:6f28a5af352c4f4457c7fbe0dfdd08e2f92e7a2c4a526e334c4f1a14dd4c82cc`.

These identify local image-store artifacts, not published GHCR digests.
Payment has frozen dependency versions; no new complete Trivy scan is claimed
here. Build-root/pip notices and upstream npm/MongoDB deprecations were not suppressed.

## Assignment deviations and remaining gates

- Reuses local kind `capstone-rollback-lab`, isolated by namespaces, rather than
  the same AWS cluster as Capstone1. Production Voting App and AWS remain untouched.
  This avoids deploying beyond existing capacity or an unauthorized paid resize.
- Owner-approved independent configurations/drill preparation replace unavailable
  instructor starter files and instructor-led simulation. Disclose this deviation.
- An own Robot Shop fork, successful shopping flow, four-service RED dashboard,
  service/level log search, Jaeger retrieval, delivered Slack alert and actual
  incident/postmortem still need genuine evidence.
- Payment gateway is simulated locally; never describe it as a real payment.

## Capture before final submission

1. Helm chart/release versions, namespaced Pod status and exact image IDs.
2. Actual catalogue → cart → payment request/order ID and sustained upstream load result.
3. Prometheus series for all focus services and exported Grafana dashboard with real data.
4. Loki query/result demonstrating service and level labels.
5. Jaeger trace ID, service/duration and actual retrieval response.
6. Alert evaluation and, only when configured and authorized, Slack firing/resolution.
7. Incident timestamps, impact, root cause, mitigation and verified recovery.

Submit the reviewed repository commit and this index with sanitized evidence.
Confirm newly added files are uploaded before sending GitHub links. Exclude
kubeconfigs, tokens, state, webhooks and private credentials. Prepared configuration
or a running collector is not proof of end-to-end telemetry. No fabricated screenshots.
