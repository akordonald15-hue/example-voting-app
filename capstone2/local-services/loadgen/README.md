# Real upstream Locust generator

Uses the copied upstream task logic with one explicit adaptation: each load user registers a fresh synthetic account using an in-memory random password, instead of relying on upstream hardcoded sample accounts. Credentials are never printed or persisted by this adapter. The upstream source is retained separately for provenance; `entrypoint.sh` is unchanged. No Instana import exists in these files. Python 3.12 Debian slim replaces Alpine to avoid carrying the previously identified musl package; this does not establish a clean image scan. Actual pinned-base inspection returned Python 3.12.14 and glibc 2.41.

`dependency-resolution.json` records the actual PyPI wheel resolution. Regenerate `../../loadgen-requirements.lock` with `python lock_from_report.py`, review it, then build from the repository root:

```sh
docker build -f capstone2/loadgen.Dockerfile -t capstone2-loadgen:local capstone2
docker run --rm --network none --entrypoint locust capstone2-loadgen:local --version
docker run --rm --network none --entrypoint locust capstone2-loadgen:local -f robot-shop.py --help
```

After all application services are healthy, the intended isolated Job uses `HOST=http://web:8080`, `NUM_CLIENTS=1`, `RUN_TIME=5m`, `ERROR=0`, `SILENT=0`. Set `activeDeadlineSeconds: 360`, `backoffLimit: 0`, `restartPolicy: Never`; request 50m CPU/64Mi RAM and limit 200m CPU/256Mi RAM. Disable service-account token mounting and use non-root/read-only/capability-drop settings. No public target or production Voting App endpoint is permitted.

This workload performs real business operations against disposable Robot Shop data, including ratings and payment requests. Do not run it against production. Upstream logic needs all supporting services (user, shipping, ratings and payment included). One randomized user is steady low load but does not guarantee every path within five minutes; separately capture a deterministic payment request if needed for trace evidence.

No traffic is initiated by the documented `--version`/`--help` import checks.

## Explicit browser shipping profile

`SHIPPING_PROFILE=upstream` remains the default and retains random country plus
the original `/cities/{country}` bulk endpoint. Earlier failures remain evidence;
do not relabel a later successful profile as an unchanged upstream load pass.

For this memory-constrained local demonstration, `SHIPPING_PROFILE=browser`
uses the same `/match/{country}/{prefix}` autocomplete route as the storefront.
It deliberately includes US, India and Great Britain, using `new`, `new` and
`lon` prefixes; all subsequent shipping calculation, cart confirmation and payment
requests are unchanged. This limits response sizes without changing database data,
skipping payment, adding retries or increasing the proxy timeout. It changes the
load distribution and is an explicit derivative profile, not a fix to bulk-city API.

Three dependency-free tests verify both route profiles and visible failures for
missing results/invalid profiles:
`python -B capstone2/local-services/loadgen/test_shipping_profile.py -v`.
All3 passed. Actual read-only autocomplete probes returned200 for all3 countries;
see [Shipping diagnosis](../../evidence/runtime/shipping-reliability.md).
The later browser-profile Job `robot-shop-loadgen-browser-205032` completed with
151requests/zero failures and eight order IDs: [actual result](../../evidence/runtime/loadgen-browser-summary.json).
It used the cache-only derivative image with no dependency installation. This
separate one-user3minute result does not replace or conceal the earlier original
upstream124/126 result. Runtime use requires those updated image bytes, not merely
an env change on an older image.

## Actual local verification, 2026-10-26

- Docker build completed with hash verification for all 37 locked dependencies.
- `locust --version` returned Locust 2.47.0, Python 3.12.14.
- `locust -f robot-shop.py --help` succeeded with no network, read-only filesystem, dropped capabilities, no-new-privileges and 256Mi memory limit. It imported the actual upstream task module without sending traffic.
- `python -m pip check`: no broken requirements found. Pip printed its non-writable home-cache warning; not suppressed.
- Evidence: `version-evidence.txt`, `help-evidence.txt`, `dependency-resolution.json`.
- Local image ID: `sha256:961dba08f585daae3be7bad335ec8782633634f4c570be06fb0d02be790c1b5c`; size 60727784 bytes; final user app (UID1000).
- No load run or runtime vulnerability scan was performed by this build task. No image was pushed.
