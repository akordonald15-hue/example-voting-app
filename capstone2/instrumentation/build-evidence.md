# Instrumented Cart and Catalogue local build evidence

Actual local verification, 2026-10-26. No image publication or cloud operations.

- Official npm registry metadata and integrity values recorded in `npm-metadata-receipt.json`.
- Node 24.22.1 satisfies the selected OpenTelemetry packages' Node >=22.15 requirement.
- `instrument_robot.py` removes Instana from generated code/dependencies, installs OpenTelemetry before HTTP/Express, and integrates RED middleware.
- Cart's existing `items_added` counter remains at the same `/metrics` endpoint.
- Cart's deprecated `request` dependency replaced with native fetch; Redis upgraded to callback-compatible 3.1.2 to fix GHSA-35q2-47q7-3pc3.
- Exact dependency locks generated with npm; both final lock resolutions reported zero npm audit vulnerabilities. This is not a Trivy/runtime-image scan.
- Both Docker builds completed using the digest-pinned Node base and non-root final user `node`.
- Three RED middleware HTTP tests passed.
- Both image smoke tests ran with read-only filesystem, all capabilities dropped, no-new-privileges, 192 MiB memory limit, and no network. HTTP health returned 200 with dependency flags false (expected without Mongo/Redis). RED metrics were exported; Cart counter preserved.
- Real OpenTelemetry trace IDs/span IDs appeared in application request logs. Export and retrieval from Jaeger remain an integration-test gate, not demonstrated by the isolated smoke test.
- MongoDB driver deprecation and npm deprecated-package warnings remain; neither was suppressed.

Local image IDs from `docker image inspect`:

| Image | ID | Size bytes |
|---|---|---:|
| `capstone2-cart:local` | `sha256:4c68d196bcb5576d4b42711b5396df8ce82eaf3690a510130d0bc4b0f0069982` | 74185498 |
| `capstone2-catalogue:local` | `sha256:3254cccd8010fb67e68d1722ccc6496e760632c7ea62cfd21824edbe6558f7b8` | 73585104 |

These local IDs are not a claimed published registry digest. Integration into a complete Robot Shop environment and private registry publication were not performed by this build task.

## Readiness correction, 2026-10-26

Added `/ready` separately from `/health`: readiness returns 503 until the dependency connection flag is true and 200 afterward. `/health` retains its upstream liveness behavior. Images rebuilt from cached dependency layers; no registry download or package changes.

Updated local IDs (supersede the image IDs above):

- Cart: `sha256:b04e18ce689f1b3b319bedb8fdcd2bb9904d0ae8720515161d69a3e2e21c8795`
- Catalogue: `sha256:8d44016a0e68fefde17fc525f6c96cb824b59628118a316051d9d85a7c9f7de6`

Both hardened network-isolated smoke tests verified `/health` 200, `/ready` 503, RED metrics, and the preserved Cart counter. Evidence: `cart-readiness-smoke.json` and `catalogue-readiness-smoke.json`. Successful dependency-backed readiness remains a runtime integration check.
