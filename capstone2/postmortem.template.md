# Robot Shop incident review — incomplete until actual drill

Status: template only. No incident outcome is asserted by this document.

- Environment/context and source commit:
- Start, detection, acknowledgement, mitigation and recovery times (UTC):
- Affected synthetic transaction and measured impact:
- Probe sample count, gaps and budget consumed:
- Trigger: independently designed local Catalogue replica-loss exercise.
- Expected failure versus actual observed failure:
- Detection evidence: Prometheus alert labels/state and query receipt:
- Notification evidence: actual Slack firing/resolved links, or **not delivered**:
- Investigation: matching Loki query and Jaeger trace IDs, or missing evidence:
- Mitigation: restore the recorded Catalogue replica count, without database edits.
- Recovery evidence: rollout, actual product HTTP200, alert resolution:
- Unaffected systems: verify scope; do not infer AWS health from local results.

## Timeline

| UTC | Observation/action | Evidence path |
|---|---|---|
| Fill from real timestamps | | |

## Contributing factors and learning

Describe system conditions and safeguards without attributing fault to people.
Separate the deliberate failure trigger from any unexpected environment issue.
Record missing telemetry as a finding, not successful detection.

## Follow-up actions

| Action | Owner | Due date | Verification |
|---|---|---|---|
| Fill after review | | | |

Disclose that this independent local exercise differs from the instructor-led,
shared-AWS-cluster scenario. Retain failed attempts and avoid a full-hour SLO claim
unless the evidence actually covers that window.
