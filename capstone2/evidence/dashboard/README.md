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
