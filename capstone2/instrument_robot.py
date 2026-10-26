"""Prepare actual cart/catalogue OTEL SDK builds; never synthesize trace evidence.

Requires prepared upstream source and an operator-reviewed exact dependency version
map. Dependency locks, builds, scans and a real cross-service trace remain gates.
"""
import json
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent
PACKAGES = ("@opentelemetry/sdk-node", "@opentelemetry/auto-instrumentations-node",
            "@opentelemetry/exporter-trace-otlp-http", "@opentelemetry/api")
TELEMETRY = '''// Load before express/http/mongodb/redis. No Instana agent is imported.
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
'''

def main():
    versions = json.loads((ROOT / "otel-versions.reviewed.json").read_text())
    if set(versions) != set(PACKAGES) or not all(re.fullmatch(r"\d+\.\d+\.\d+", v) for v in versions.values()):
        raise ValueError("STOP: reviewed exact OTEL versions required")
    for role in ("cart", "catalogue"):
        source = ROOT / "upstream-source" / role
        destination = ROOT / "instrumented" / role
        destination.mkdir(parents=True, exist_ok=True)
        package = json.loads((source / "package.json").read_text())
        package["dependencies"].pop("@instana/collector", None)
        package["dependencies"].update(versions)
        if role == 'cart':
            package['dependencies'].pop('request', None)
            package['dependencies']['redis'] = '3.1.2'
        # Existing upstream dependency vulnerabilities must be remediated before deployment.
        (destination / "package.json").write_text(json.dumps(package, indent=2) + "\n")
        text = (source / "server.js").read_text().replace("require('@instana/collector')", "require('./telemetry')")
        text = re.sub(r'\binstana\b', 'telemetry', text)
        dependency = 'redisConnected' if role == 'cart' else 'mongoConnected'
        text = text.replace("app.get('/health', (req, res) => {", "app.get('/ready', (req, res) => { res.status(" + dependency + " ? 200 : 503).json({ ready: " + dependency + " }); });\n\napp.get('/health', (req, res) => {")
        if role == 'cart':
            text = text.replace("const request = require('request');", "// Native fetch replaces the unmaintained request/form-data dependency.\nconst request = (url, callback) => { fetch(url).then(async response => callback(null, { statusCode: response.status }, await response.text())).catch(error => callback(error)); };")
        text = text.replace('const app = express();', "const app = express();\nconst red = require('./red.cjs').createRedMetrics('" + role + "');\napp.use((req, res, next) => {\n  if (req.path === '/metrics') return next();\n  return red.middleware(req, res, next);\n});")
        if role == 'cart':
            text = text.replace('res.send(register.metrics());', "res.send(register.metrics() + '\\n' + red.render());")
        else:
            text = text.replace('app.use(expLogger);', "app.get('/metrics', (req, res) => { res.type('text/plain'); res.send(red.render()); });\napp.use(expLogger);")
        (destination / "server.js").write_text(text)
        (destination / "telemetry.js").write_text(TELEMETRY)
        shutil.copyfile(ROOT / 'instrumentation' / 'red.cjs', destination / 'red.cjs')
        shutil.copyfile(ROOT / "instrumented.Dockerfile", destination / "Dockerfile")
    print("PREPARED sources; create/review locks, build/scan/test before image approval")

if __name__ == "__main__":
    main()
