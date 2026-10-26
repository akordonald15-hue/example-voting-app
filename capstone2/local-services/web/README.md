# Local Web adapter

Reuses the pinned upstream static storefront with a dependency-free Node24 HTTP
static server and API reverse proxy on port8080. No Instana binaries/imports or
browser injection. `/health` and `/metrics` export real request/status/duration.
Unlike upstream Nginx, it has no nginx_status endpoint, caching directives or SSI;
the only upstream SSI include was optional Instana browser instrumentation.
Proxy service host environment variables follow upstream; Ratings remains port80.
This is a local demonstration adapter, not a production Nginx equivalent.

Build: `docker build -t capstone2-web:local capstone2/local-services/web`.
Smoke test: mount this directory read-only at `/tests` and run
`node /tests/smoke.cjs` with working directory `/app` inside the built image.
