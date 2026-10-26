// Load before express/http/mongodb/redis. No Instana agent is imported.
const { NodeSDK } = require('@opentelemetry/sdk-node');
const { getNodeAutoInstrumentations } = require('@opentelemetry/auto-instrumentations-node');
const { OTLPTraceExporter } = require('@opentelemetry/exporter-trace-otlp-http');
const { trace, context } = require('@opentelemetry/api');
const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter(),
  instrumentations: [getNodeAutoInstrumentations({ '@opentelemetry/instrumentation-fs': { enabled: false } })]
});
let started = false;
function init() { if (!started) { sdk.start(); started = true; } }
init.currentSpan = () => ({ annotate: (key, value) => {
  const span = trace.getSpan(context.active());
  if (span) span.setAttribute(key, value);
}});
process.once('SIGTERM', () => sdk.shutdown().finally(() => process.exit(0)));
module.exports = init;
