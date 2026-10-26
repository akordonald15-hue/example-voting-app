# Grafana provisioning and panel query evidence

Captured read-only October26 in local kind `capstone-rollback-lab-control-plane`.
AWS was not contacted or modified. Credentials were used only in process memory,
never printed, placed in command arguments or written to the evidence files.

- [grafana-api.json](grafana-api.json): actual health, dashboard search, safe
  datasource metadata and full provisioned dashboard response.
- [robot-shop-exported.json](robot-shop-exported.json): dashboard JSON extracted
  from that actual API response for inspection/import.
- [prometheus-panel-queries.json](prometheus-panel-queries.json): actual Grafana
  datasource-proxy Prometheus query responses and UTC timestamp.

Grafana13.2.4 reported database `ok`; dashboard UID `capstone2-robot-shop`
was provisioned with seven panels. Prometheus, Loki, Jaeger and Alertmanager
datasource definitions exist; definitions alone do not prove backend connectivity.

At20:09UTC, actual totals/rates/p95 existed for Catalogue, Cart and Web. Payment
was absent from request metrics at this snapshot; the load test had not yet
completed a payment. This is partial dashboard evidence, not a four-service RED
pass. All targets UP is a separate scrape-health claim and cannot replace this.
Zero error series may be absent before an error occurs; missing data is not zero.

Measured availability was0.87156 including earlier startup failures, below99%.
Error-budget remaining was negative because the expression only caps its upper
bound; this indicates exhausted budget. JSON retains exact values, including Web
error rate and a10-second Web p95. Do not present this window as healthy.

No browser screenshot was generated. Installed executables did not provide a
verified credential-safe automation path; API responses are the genuine evidence.

## Later refresh after successful checkout

[Earlier successful Grafana query capture](prometheus-panel-queries-20261026T2009Z.json)
is retained separately. The latest `prometheus-panel-queries.json` records a
20:32UTC refresh failure (`URLError`), not clean/empty results. Grafana had2/3
Ready containers; its own container was unready and a direct five-second health
request also timed out. No endpoint had been routed through its Service.
No restart or settings change was attempted by this evidence task.

To distinguish application metrics from Grafana availability,
[direct Prometheus queries](prometheus-direct-20261026T2034Z.json) were captured
read-only from the same local node. These returned real request totals, rates and
p95 for **all four focus services**, including Payment total4 and p95 approximately
0.475seconds. Cart had restarted between captures, so its raw counter reset;
do not compare raw totals as cumulative across process replacement.

This establishes four-service metric presence in Prometheus and queries matching
the provisioned dashboard. It does **not** establish a working rendered Grafana
dashboard at this later instant. Catalogue/Web zero5xx series were present;
missing Cart/Payment5xx series are not invented zeros. Availability was0.90833,
still below99%, with negative remaining budget. Web p95 remained approximately
6.67seconds. Keep those genuine limitations visible.

## Final bounded post-load refresh

One later read-only refresh succeeded after the browser-profile load completed:
[Grafana API receipt](grafana-api-20261026T2056Z.json),
[authenticated panel queries](grafana-panels-20261026T2056Z.json) and
[direct Prometheus comparison](prometheus-direct-20261026T2056Z.json).
The filenames identify this capture batch; exact query UTC timestamps are inside.
No earlier success/failure receipt was replaced.

Grafana again reported database `ok`, with the provisioned dashboard present.
All four services now had real request totals, rates and p95 returned through
Grafana itself. At this snapshot Payment total was26 and its p95 was5.75seconds;
Web p95 was approximately0.95seconds. This demonstrates working dashboard-query
data, not a browser screenshot or universal latency-objective success.
Availability remained0.96667 below99%, with negative budget remaining. Missing
Cart/Payment5xx series remain missing rather than invented zeros.

No new browser tooling was installed or credential-bearing browser profile
created under the constrained local memory budget. No screenshot is claimed.

## Slack status

Local monitoring routes to `local-no-delivery`, with no Slack secret mounted.
A name-only lookup found no `capstone2-slack` Secret in local observability.
The Alertmanager custom resource has one desired replica; that does not prove
a healthy Pod or delivered messages.

Separate prepared values reference `capstone2-slack/webhook`, channel
`#capstone-alerts`, resolved messages and a runbook annotation. This is design,
not delivery evidence. A real Slack firing/resolved demonstration remains
incomplete and needs an approved webhook through a protected local Secret,
never Git, command output or chat logs.
