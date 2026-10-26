# Robot Shop lab availability SLO and error-budget policy

Scope: catalogue product-list HTTP transaction via web → catalogue → MongoDB,
probed every 30 seconds from Blackbox Exporter. Success requires HTTP200 within
5 seconds and `sku` in the response. This is synthetic path availability, not
checkout/payment correctness or real-user availability.

**Lab SLO: 99% over a rolling one-hour window**, with 36 seconds equivalent
unavailability (1.2 failed 30-second probes) of budget. Prometheus keeps two
hours; a full hour of data is required before an SLO attainment claim. Finite
samples mean the permitted failed-probe count is discrete. Report sample count
and coverage. Missing probe/scrape data is UNKNOWN, never silently successful;
`RobotShopProbeMissing` pages separately. No production-grade 30-day claim.

Budget consumption = `(1 - measured availability)/0.01`; remaining budget is
`1 - consumption`, negative when exhausted. Alert when the synthetic transaction
fails continuously for one minute. Route to
the approved Slack channel with only service/severity/summary; no raw request
headers, tokens, customer records or secret-bearing logs. Verify firing AND
resolved notifications; configuration alone does not prove delivery.

When the availability alert fires or budget is exhausted: freeze Robot Shop feature changes
and traffic escalation, acknowledge, inspect probe/metrics/logs/traces, identify
the approved recent change and restore only that change. Do not change Voting
App, delete storage or automatically roll back an unverified revision. Resume
changes after recovery, sufficient healthy coverage, incident review and owner
approval. Record intentional simulations as budget-consuming events; never
erase inconvenient samples. Planned downtime is not excluded.

The instructor PDF specifies availability and a one-page error budget but no
numeric window/target. This lab-sized target is a proposal, not measured attainment.
