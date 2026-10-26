# Robot Shop alert response

This runbook is prepared; its GitHub URL becomes live only after approved commit/push.
Do not use it as authorization to mutate resources.

1. Acknowledge the Slack alert. Confirm target is Robot Shop and telemetry is fresh.
   Note UTC time, alert labels, probe sample coverage and last known good request.
2. Check private Grafana dashboard and Blackbox target; compare the failing URL to
   actual web/catalogue/MongoDB health. Missing telemetry is UNKNOWN, not success.
3. Use Loki `{namespace="robot-shop",service="catalogue",level="error"}` and the
   corresponding cart/web/payment logs. Unknown levels need parser review. Never
   paste raw credential/customer-bearing records into Slack/submission.
4. Inspect one real Jaeger trace if available. Do not infer successful tracing from
   a healthy collector listener or generate fake business spans for evidence.
5. During the independently designed drill, mitigate the specific approved failure first:
   restore the affected Robot Shop workload's recorded setting/replica/image under
   the drill approval. No Voting App, database/PVC, infrastructure or unverified
   Helm rollback changes. If no restoration action is authorized, escalate to owner.
6. Require successful business requests, probe recovery, healthy pods and resolved
   Slack alert. Record exact downtime and budget consumed. Watch existing Voting
   App health; node-wide pressure requires stopping the lab, not deleting its data.
7. Preserve sanitized metrics/log queries/trace IDs/timeline and complete a blameless
   postmortem. Identify this as an independent alternative to the PDF's instructor-led exercise.
