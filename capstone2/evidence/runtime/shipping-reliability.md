# Shipping bulk-city timeout diagnosis

Read-only local kind inspection October26,2026. No database writes, schema changes,
database stops, kind/Docker restarts, AWS calls or production changes.

The original load result remained124/126 with two city-request timeouts. A complete
11-request checkout had already passed independently; neither result is overwritten.

## Observed contributing causes

- Upstream `/cities/{code}` materializes and serializes every matching city. A
  read-only SQL count showed India39813, US141989 and Great Britain17708 rows.
  A `country_code` BTREE index already exists; adding an index is not the fix.
- Direct Shipping service requests for India, US and Britain each exceeded22seconds
  in this diagnostic window, bypassing Web's15-second upstream timeout. Thus this
  was not solely a proxy or service-DNS error.
- Shipping cgroup CPU statistics showed2371 throttled periods of3992 and655seconds
  cumulative throttling, compared with125seconds CPU usage since container start.
  Counters are cumulative, not precise per-request attribution.
- Shipping logged Hikari thread starvation/clock-leap with a59-second housekeeper
  gap during local host pressure. MySQL was CPU-limited to200m; Shipping500m.
  No single bottleneck is proven by these cumulative observations. Large results,
  CPU contention and low host memory are evidence-backed contributors.

The storefront itself uses bounded `/match/{country}/{prefix}` autocomplete.
The original upstream load generator instead downloads complete city lists.

## Minimal local improvement

Added an explicit opt-in browser-style shipping profile to the derivative load
generator; default upstream behavior remains intact. The browser profile includes
the problematic countries, rather than hiding them, and leaves shipping/cart/payment
business operations unchanged. No automatic retries, result suppression, country
database pruning or longer proxy timeout were added.

[Actual bounded read probes](shipping-browser-profile-probe.json),20:40UTC:

| Route | HTTP | Cities | Response bytes | Seconds |
|---|---:|---:|---:|---:|
| `/match/in/new` |200 |7 |823 |1.186 |
| `/match/us/new` |200 |9 |1159 |2.805 |
| `/match/gb/lon` |200 |9 |1315 |0.408 |

Three routing/failure unit tests passed. The subsequently authorized browser-profile
run completed: [summary](loadgen-browser-summary.json), [Job result](loadgen-browser-job-result.json),
[Pod result](loadgen-browser-pod-result.json), [Locust log](loadgen-browser-3m.log).
It recorded **151requests, zero failures, eight completed payment orders**, one user
for3minutes. Job started20:50:33UTC and completed20:53:46UTC (193seconds including
startup/shutdown); Pod Succeeded, exit0, zero restarts. No retry or cleanup/removal
occurred. The Job/Pod remain available for inspection.

The normal rebuild was stopped when its dependency layer missed cache under
networknone. A separately approved tiny [derivative Dockerfile](../../local-services/loadgen/browser.Dockerfile)
then copied only the updated script onto the verified existing locked-dependency
base, with networknone/pullfalse and no dependency installation. See [build identity](loadgen-browser-build.json)
and [exact Job](loadgen-browser-job.json). Binary-stdin import avoided a failed
Docker-copy path; no unrelated images or volumes were removed.

This demonstrates the explicit browser profile, not resolution of the original
bulk endpoint's latency/scale limitations. A production
fix would need bounded API pagination/query limits and representative load testing,
or adequate capacity; it should not be improvised by changing stored city data.
