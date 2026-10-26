# Local Shipping and Cart remediation

Scope: local kind only; no AWS, production or database changes.

Observed failures before correction: Shipping `/codes` exceeded the15-second
Web upstream inactivity timeout; one Cart product-add request also timed out.
Shipping logs recorded handler entry and historical Hikari thread-starvation
warnings. A live Java thread dump during the request showed the connection-adder
thread in Inet6AddressImpl.lookupAllHostAddr from MySQL StandardSocketFactory.
CPU counters showed21188throttled periods out of40772. These support DNS/scheduling
latency; they do not independently isolate a single cause.

A separate definite endpoint fault existed: upstream Shipping constructs its
Cart URL from CART_ENDPOINT and defaults to port80, but this chart's Cart Service
listens on8080. This would affect shipping confirmation even after `/codes` works.

Corrections in chart and targeted local Deployment patches:
- Shipping DB_HOST uses absolute `mysql.robot-shop.svc.cluster.local.`.
- Shipping CART_ENDPOINT uses `cart.robot-shop.svc.cluster.local.:8080`.
- Cart CATALOGUE_HOST uses absolute `catalogue.robot-shop.svc.cluster.local.`.
- Local-demo Shipping/Cart CPU limits are500m instead of200m; requests/memory
  remain unchanged. Non-local CPU limits remain200m.

The Web timeout was not increased, errors were not filtered, and dependencies
were not bypassed. Runtime changes used targeted local Deployment patches; no new
Helm revision is asserted. Source renders match these intended settings, with an
offline regression test for the dependency endpoints and local CPU limit.

Result: shopping_smoke.py completed11HTTP200requests including registration,
login, catalogue, Cart, shipping confirmation and simulated Payment. Order ID:
18208816-0fa1-450a-b4f8-367c09239788. Exact durations and response statuses are in
`evidence/runtime/shopping-flow.json`. The payment gateway is the local mock;
this is not a financial transaction. Earlier65/70 load evidence stays intact.

Reproduce: `python capstone2/shopping_smoke.py` (explicit local node identity
check; bounded requests; synthetic credentials kept in process memory).
The subsequent bounded one-user load run is recorded separately; inspect its
actual request counts and Job termination before declaring load-test success.

Later run:124/126requests succeeded (98.41%); two Shipping city-list timeouts remained. Successful order responses were recorded. Locustexit1 and JobFailed/BackoffLimitExceeded preserve fail-closed behavior; no automatic retry. Capacity/performance work remains before calling this production-ready.
