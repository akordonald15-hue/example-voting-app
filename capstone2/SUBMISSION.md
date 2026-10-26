# Robot Shop submission evidence index

Checkpoint: October 26, 2026. Deadline: October 27, 12:00 WAT.

| Requirement | Actual checkpoint | Evidence |
|---|---|---|
| Pinned source/chart | Prepared from upstream `55292e2199f2fb00a165b1f7d3045fe7f8922038` | [Receipt](upstream-receipt.json), [chart](robot-shop/) |
| Four focus builds without active Instana | Web, Catalogue, Cart, Payment local builds completed | [Cart/Catalogue](instrumentation/build-evidence.md), [Web](local-services/web/), [Payment](local-services/payment/) |
| RED instrumentation | Real counter/histogram export passed isolated tests | [Middleware tests](instrumentation/test-red.cjs), [Web smoke](local-services/web/smoke.cjs), [Payment smoke](local-services/payment/smoke.py) |
| Trace instrumentation | Cart/Catalogue request trace IDs observed; Payment actual OTLP protobuf POST captured locally | Build receipts and Payment smoke; not yet a retrieved Jaeger trace |
| Application deployment | Local kind installation underway; no all-Ready/checkout claim yet | Add genuine runtime receipts after verification |
| Steady upstream load | Three-minute one-user run:70requests,65successes,5failures (7.14%); registration/login200; checkout blocked at Shipping | [Local load generator](local-services/loadgen/) |
| Prometheus/Grafana | Prometheus returned all four focus targets UP=1 and real RED series; Grafana 3/3 Ready and health API database=ok; seven-panel dashboard exported and real panel queries saved; no screenshot | [Local values](monitoring-local.values.yaml) |
| Fluent Bit/Loki | Real Fluent Bit to Loki Web query returned five lines labelled service=web and level=info | [Configs](observability/config/) |
| Jaeger | Real Catalogue HTTP spans retrieved; see jaeger-v3-catalogue-traces.ndjson | [Auxiliary chart](observability/) |
| SLO/error budget | Written policy prepared, sustained measurement pending | [SLO](SLO.md) |
| Slack | Rule/runbook prepared; actual firing/resolved delivery not demonstrated | [Runbook](runbook.md) |
| Incident/postmortem | Local catalogue-loss drill recorded pending then firing alert; restoration/recovery receipts captured separately | Record actual timeline, mitigation and recovery before finalizing |

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
- An own Robot Shop fork, successful shopping flow, four-service Grafana dashboard,
  delivered Slack alert and actual
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

Runtime receipts include initial failures as well as subsequent successes. See `evidence/runtime/jaeger-v3-catalogue-traces.ndjson`, `loki-web-info-query.json` and `prometheus-up.json`. No complete checkout, delivered Slack alert or successful fresh Trivy scan is claimed.

Latest closeout: [registration investigation](registration-investigation.md), [load summary](evidence/runtime/load-summary.json), [dashboard evidence](evidence/dashboard/README.md), [both-capstone rubric](../docs/final-rubric-status.md). Payment request series were absent in the captured dashboard query; do not claim all four business-service panels contain data.

## Later remediation checkpoint

The earlier65/70 run and unsuccessful Job completion remain historical evidence. A later local11-request smoke flow returned HTTP200 throughout and generated a simulated order; see [shopping receipt](evidence/runtime/shopping-flow.json) and [remediation](shipping-cart-remediation.md). The subsequent one-user load is separate evidence and retains all failures.

Direct Prometheus queries now contain all four focus services, including Payment. Grafana dashboard provisioning was previously verified, but the latest Grafana refresh became unavailable. Do not substitute direct metrics for a fresh rendered-dashboard pass. See the dated captures in [dashboard evidence](evidence/dashboard/README.md).

[AWS capacity/approval plan](aws-deployment-plan.md) compares resize versus a worker; existing t3.medium remains NO-GO. [Capstone1 automation prerequisites](../docs/capstone1-automation-closeout.md) passed local tests but production activation remains unapproved and not demonstrated. Slack and fresh Trivy remain blocked; no credentials were provisioned or extra containers stopped.

Final later load result: **124/126 successful requests (98.41%)**, two Shipping city-list502s. Locust exited1; JobFailed/BackoffLimitExceeded; no retries. Successful simulated orders were recorded, but this is not an error-free load pass. [Exact summary](evidence/runtime/load-e2e-summary.json), [retained log](evidence/runtime/loadgen-e2e.log).

## Browser-equivalent bounded load — verified success

A separately labelled browser profile uses the storefront autocomplete route for India, US and Britain instead of downloading complete country city lists. Actual run: **151requests,0failures,8completed simulated payment orders**,1user/3minutes,193seconds total Job elapsed; Job/PodSucceeded,exit0,zero restarts. See [summary](evidence/runtime/loadgen-browser-summary.json) and [diagnosis/profile disclosure](evidence/runtime/shipping-reliability.md). The upstream bulk-city profile still has a known latency limit; earlier65/70 and124/126 failure evidence is retained. No production/AWS load test is claimed.

[Exact worker Terraform proposal](../terraform-worker/README.md): liveplan17add/0change/0destroy, five new rules attach to existing serverSG. Regionalquota32vCPU and$111.93remainingcredits verified read-only; creditexpiry/applicability unverified. Workercreation, IAMpermissionupdates, agentjoin andAWSdeployment await separate approvals.

Latest post-load Grafana refresh passed: authenticated dashboard/panel queries returned request totals, rates and p95 for all four focus services, including Payment. [Dated dashboard receipts](evidence/dashboard/README.md) retain earlier failures. Availability remained below99%; no screenshot or SLO-attainment claim.
