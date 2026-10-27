# Incident evidence and blameless postmortems

## Demonstrated: local catalogue-loss drill

Environment: local kind only, October26. At19:33:41UTC the approved controller scaled Catalogue's single replica to zero. Availability probe failed; RobotShopUnavailable transitioned pending→firing. At19:36:20UTC the original replica was restored by finally cleanup. A later probe returned1; subsequent alert evaluation returned an empty active-alert list. This tests detection/recovery of a local single-replica service, not AWS recovery or real Slack notification delivery.

Evidence: [timeline](../capstone2/evidence/runtime/incident-timeline.json), [firing sample](../capstone2/evidence/runtime/incident-sample-3.json), [recovery](../capstone2/evidence/runtime/incident-recovery.json), [resolution](../capstone2/evidence/runtime/incident-alerts-followup.json), [original postmortem](../capstone2/postmortem-local.md).

Cause: deliberate loss of the only Catalogue replica. Contributing condition: single-replica demo capacity. Impact: synthetic catalogue-path unavailability; no production Voting App/data-store changes. Detection worked. Slack delivery was absent; incident-correlated logs/full checkout traces were not demonstrated. Follow-ups: retain failure samples, verify full transaction recovery, provide approved Slack delivery test, review redundancy only with capacity/approval. No blame assigned to an operator for the intentional simulation.

## Observed: blocked Catalogue publication

Web and Cart were successfully published. Catalogue's one approved Phase2C push returned1 after a registry PUT failed because Docker Desktop could not resolve ghcr.io. Partial content remained; the approved tag was absent. No retry was performed. Payment/Loadgen were not reached. Read-only tests later showed intermittent host/container DNS/HTTPS timeouts; the underlying router/filtering/resource/network cause remains unresolved. No package cleanup, credential change or Docker reset was performed.

[Sanitized DNS/publication summary](evidence/capstone2-publication.json) includes source receipts/hashes. This is an observed workstation delivery interruption, not a performed AWS incident drill. Follow-up is stable connectivity plus separate authorization for one exact-byte retry with captured diagnostics. Publication work is now stopped for submission closeout.
