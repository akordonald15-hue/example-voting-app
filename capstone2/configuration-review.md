# Observability configuration review — 2026-10-26

**Deployment NO-GO; local preparation only.** No production operation performed.

## Provenance

The existing observability files are locally prepared drafts, not verified
instructor originals. Repository filename/content searches and relevant Downloads
filename searches did not find separate instructor values/configs. The original
assignment PDF pages 6–9 describes the separately supplied configurations but
does not supply their contents. Unrelated ZIP archives were not opened. Obtain
the instructor's actual starter bundle or confirmation that these drafts are
acceptable; do not silently replace or relabel them.

## Configuration findings

| Area | Implemented / offline evidence | Still unverified or blocked |
|---|---|---|
| Fluent Bit | Read-only `/var/log/pods`; tail only `robot-shop_*/*/*.log`; CRI wrapper parser; container-path service label; bounded level labels, including warning→warn normalization | Actual K3s log layout, file access, CRI partial/multiline handling, real service/level samples and Loki ingestion. Container name is a service proxy only where chart names match. Host mount exposes more files than the configured tail selection. |
| Blackbox | Required auxiliary Deployment/Service on 9115; configured `http_success` module and Prometheus relabel target match | Image pins, successful probe response and scraped `probe_success`; a missing exporter is missing telemetry, not availability success. |
| Slack | Secret name `capstone2-slack`, key `webhook`, mount `/etc/alertmanager/secrets/capstone2-slack/webhook`; no webhook value in values | External Secret provisioning under separate approval; pinned official chart render, `amtool` validation, Slack firing/resolved delivery. |
| Jaeger | Collector `otlphttp/jaeger` uses `http://jaeger:4318`; Jaeger OTLP HTTP receiver and Service expose 4318 | Exact-image runtime config validation, application SDK compatibility and one genuine request trace. TCP readiness does not prove trace ingestion. |
| RED dashboard | Draft queries present | Required four-service request/error/latency series are not exported. Existing cart `items_added` alone cannot fulfill RED requirements. |
| Loki | Single-instance filesystem/TSDB draft; ephemeral bounded storage | Exact-image config validation, writable directories and actual searchable logs. No durable retention guarantee. |

Only log-level cardinality was corrected in this review: arbitrary string levels
now become `unknown`. No instructor file was overwritten. Added offline tests
cover Blackbox, Slack mount, Jaeger Service/receiver and Fluent Bit selection/mount
contracts. These test rendered configuration, not live delivery or binary parsing.

## Capacity gate

Current known instance is t3.medium (nominal 2000m CPU, 4GiB RAM).
Declared requests: Voting App 450m/608Mi; Robot Shop 1200m/1956Mi;
auxiliary stack including one Fluent Bit 250m/288Mi; configured Prometheus,
Grafana and Alertmanager 175m/416Mi. Total **2075m CPU / 3268Mi memory**,
before operator/exporters, system components, load generation or headroom.
This cannot fit nominal CPU capacity as declared. Combined configured memory
limits are approximately 6640Mi; limits are not reservations but indicate OOM
risk under simultaneous load. No capacity change is authorized.

Use the existing README's four read-only capacity commands to obtain allocatable
resources, utilization and disk; no recovery inventory needs repeating. Then
review the full pinned official chart's resource budget before proposing either
measured reductions or an approved capacity change preserving production storage.

## Evidence needed before approval

1. Instructor starter bundle/provenance decision; pinned official monitoring
   chart and all image digests, security scans and version-specific config checks.
2. A feasible measured resource budget and separately approved deployment scope.
3. Disposable local application/telemetry rehearsal: real service/level logs,
   Blackbox scrape, four-service RED series, one Jaeger trace and Slack validation.
4. Separate approval for any cluster resources, Secrets, host-log access or cost.

References: [Fluent Bit Loki labels](https://docs.fluentbit.io/manual/4.1/data-pipeline/outputs/loki),
[Prometheus Operator Secret mounts](https://prometheus-operator.dev/docs/api-reference/api/),
[Jaeger OTLP HTTP API](https://www.jaegertracing.io/docs/2.1/apis/).
These support the configuration contracts; they are not exact-image runtime tests.
