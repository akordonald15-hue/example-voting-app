# Local Payment adapter

Pinned upstream business handler and RabbitMQ publisher with Instana removed.
Flask runs non-root on port8080; `/health`, `/metrics` preserve existing routes.
Added real service/status counters and latency histograms; incoming requests
generate OpenTelemetry server spans with propagated incoming context and export
OTLP HTTP to `OTEL_EXPORTER_OTLP_ENDPOINT` (default localhost:4318).
`CART_HOST`, `USER_HOST`, `AMQP_HOST`, `PAYMENT_DELAY_MS` retain upstream meaning.

`PAYMENT_GATEWAY` retains upstream default https://paypal.com/. For isolated
demonstrations explicitly configure an internal mock200 endpoint and label the
payment as simulated; do not generate dummy load against a real payment site.
The payment service remains a sample application: no financial transaction occurs.
RabbitMQ guest credentials are upstream demo defaults, never production secrets.

Build: `docker build -t capstone2-payment:local capstone2/local-services/payment`.
Flask built-in server is for this local demonstration only. Direct dependencies
are pinned; the complete installed dependency receipt is requirements.lock after
the successful build. No vulnerability-scan or complete checkout claim is made
by the service smoke test alone.
