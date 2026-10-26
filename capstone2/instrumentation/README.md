# Independent RED instrumentation adapter

Prepared locally on 2026-10-26. This is an independent alternative, not instructor-provided configuration. Derived local Cart and Catalogue images now include the adapter; no production workload was changed. See `build-evidence.md` for actual build and smoke-test results.

`red.cjs` uses only Node built-ins. It exports the existing dashboard contracts:

- `http_server_requests_total{service,status}`
- `http_server_request_duration_seconds_bucket{service,le}`
- Histogram `_sum` and `_count`, with cumulative buckets and `+Inf`.

Durations use the monotonic clock and are observed on the actual response `finish` event. Scrapes at `/metrics` are excluded. Labels contain no URL, customer identifier, exception text or request data. Only web/catalogue/cart/payment are accepted as service identities. Aborted responses that never finish are not counted; use independent blackbox probes for end-to-end availability, including disconnects.

## Integration into prepared Node services

`instrument_robot.py` copies this module into the derived Cart and Catalogue build contexts. The integration excludes `/metrics` from middleware handling so Cart can compose its existing business counter and RED exposition into one endpoint. For a service without an existing metrics route, the basic adapter use is:

```js
const red = require('./red.cjs').createRedMetrics('cart'); // 'catalogue' in catalogue
app.use(red.middleware);
```

The basic adapter owns `/metrics`; Cart's implemented wrapper instead preserves `items_added` and appends `red.render()` at its existing route. The standalone adapter adds no runtime dependency. The derived preparation process removes Instana and adds real OpenTelemetry SDK tracing separately.

Pinned/non-root Cart and Catalogue images were built and their isolated HTTP/metrics smoke tests passed. Dependency-backed traffic and Jaeger export remain integration gates. Configure Prometheus scrape targets and NetworkPolicies for both services. No deployed dashboard or full business-flow evidence is claimed by these smoke tests.

Web is Nginx and payment is Python: this Node middleware does not instrument them. Both need equivalent bounded-label instrumentation (or a separately justified ingress/proxy measurement design) and scrape configuration before the four-service RED requirement is complete. Do not label blackbox probe latency as per-service RED latency.

## Executed local validation

```powershell
node --test capstone2/instrumentation/test-red.cjs
```

Three tests passed using the local Node runtime. They exercise actual loopback HTTP 200 and 500 responses, measured durations, histogram monotonicity, cumulative totals, metrics content type, scrape exclusion and service allowlisting. They are synthetic instrumentation tests, not Robot Shop business-flow, deployed-dashboard or availability evidence.
