# Capstone 2 — Robot Shop observability

**Current submission guide:** [Robot Shop results, limitations and instructions](../submission/capstone2.md).

[Evidence index](../submission/evidence-index.md) · [matrix](../submission/requirement-matrix.md) · [architecture](../submission/architecture.md) · [postmortems](../submission/incidents.md).

Local kind demonstration only:simulated checkout;151/151browser-profile requests,8 simulated orders;earlier65/70 and 124/126failed Jobs retained. Real four-service RED/Grafana queries, Loki Web logs, Catalogue Jaeger spans and local alert/recovery receipts exist. No fabricated screenshots or successful Slack delivery claim.

Robot Shop has **not** been deployed to AWS. Worker readiness/isolation is owner-confirmed;AWS overlays are offline preparation. GHCR Web/Cart verified, three images pending after DNS instability. Fresh complete Trivy scanning remains blocked by memory. Publication/deployment work has stopped.

[Chart](robot-shop/) · [observability chart](observability/) · [SLO](SLO.md) · [runbook](runbook.md) · [provenance](upstream-receipt.json). Follow [safe reproduction guidance](../submission/reproduction.md), not historical install snippets against production.
