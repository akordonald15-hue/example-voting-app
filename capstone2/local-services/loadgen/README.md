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

## Actual local verification, 2026-10-26

- Docker build completed with hash verification for all 37 locked dependencies.
- `locust --version` returned Locust 2.47.0, Python 3.12.14.
- `locust -f robot-shop.py --help` succeeded with no network, read-only filesystem, dropped capabilities, no-new-privileges and 256Mi memory limit. It imported the actual upstream task module without sending traffic.
- `python -m pip check`: no broken requirements found. Pip printed its non-writable home-cache warning; not suppressed.
- Evidence: `version-evidence.txt`, `help-evidence.txt`, `dependency-resolution.json`.
- Local image ID: `sha256:961dba08f585daae3be7bad335ec8782633634f4c570be06fb0d02be790c1b5c`; size 60727784 bytes; final user app (UID1000).
- No load run or runtime vulnerability scan was performed by this build task. No image was pushed.
