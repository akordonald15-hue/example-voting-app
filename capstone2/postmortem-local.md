# Local Robot Shop catalogue availability drill

Environment: local kind `capstone-rollback-lab`, namespace `robot-shop`; October26,2026.
This was an independently designed local exercise, not an AWS production incident.

The baseline availability probe was1 and catalogue had one available replica.
At19:33:41UTC the controller scaled only catalogue to zero. Prometheus recorded
RobotShopUnavailable pending and then firing (sample3). At19:36:20UTC the
controller restored the original replica count in a finally block; Kubernetes
subsequently reported a successful rollout and catalogue1/1 available.
Consult `evidence/runtime/incident-recovery.json` for the final probe and alert
state; rollout readiness alone is not transaction recovery.

The deliberate cause was loss of the only catalogue replica. MongoDB and other
data stores were not changed. No AWS or Voting App commands were issued.
One replica is a single availability failure point. A short local outage is
expected in this capacity-constrained rehearsal. No full-hour SLO attainment or
precise error-budget consumption is asserted from these samples.

Detection succeeded through the availability rule. Slack delivery was not
configured or demonstrated. Real Loki Web logs and Jaeger Catalogue spans exist
in the runtime evidence, but are not represented as correlated incident traces.

Separate integration findings: the initial load Job omitted its namespace; a
trailing-slash HOST produced double-slash requests; corrected registration then
returned502. Those failure receipts are retained. A complete shopping flow and
sustained successful load remain blockers. Grafana startup initially exceeded
liveness timing; a bounded startup probe allowed it to reach3/3 Ready.

Follow-up before final submission: verify recovered transaction/probe and alert
resolution; complete successful synthetic shopping load; capture the provisioned
Grafana dashboard; deliver an approved Slack firing/resolved test. Keep this
exercise distinct from the isolated Voting App Helm rollback demonstration.

Recovery verification: the final transaction probe was1. The immediate recovery
alert sample still fired; a subsequent evaluation returned an empty active-alert
list (`incident-alerts-followup.json`), confirming resolution at that checkpoint.
Slack notification delivery remains unverified.
