# Focused musl / Actions remediation — 2026-10-26

**GO for requesting correction-push approval; no push performed.** PR #1 remains
draft at 1ef3cc6 until explicitly approved. No production or infrastructure changes.

## Security correction

Vote and Worker keep their existing immutable base digests and runtime users.
Runtime package installation explicitly pins `musl=1.2.6-r3` and matching
`musl-utils=1.2.6-r3` from the existing Alpine 3.24 repositories. Matching utilities
prevent package-revision mismatch; no libc files are copied manually. Build-stage
images remain unchanged and do not enter the runtime filesystem. Future removal
of this exact repository revision must fail the build, not silently downgrade.
The APK downloads still use the distribution's signed repository metadata; package
version pinning is not a replacement for base-image digest pinning.

Alpine 3.24's [security database](https://secdb.alpinelinux.org/v3.24/main.json)
identifies 1.2.6-r3 as fixed for CVE-2026-107891. The earlier Trivy missing-details
warning was not evidence of a rejected CVE: the [maintainer advisory](https://seclists.org/oss-sec/2026/q4/289)
describes integer overflows when libc regcomp processes untrusted regular expressions.

Actual package metadata in all three candidate images now reads 1.2.6-r3.
Vote/Worker still identify as Alpine 3.24.2 because only the required packages were
updated; Result was already Alpine 3.24.3. Release text alone is not patch evidence.

The acceptance runner adds a package gate for all three exact image IDs before
application startup. It requires the reviewed Alpine 3.24 branch and fixed musl
floor; future distro changes require explicit review. An old-image negative test
fails with `Unreviewed Alpine branch or vulnerable musl in vote` as expected.
The existing eight functional/security checks remain, plus this ninth check.

## Official upstream Actions pins

| Action/release | Verified full commit SHA |
|---|---|
| checkout v7.0.1 | 3d3c42e5aac5ba805825da76410c181273ba90b1 |
| setup-python v7.1.0 | 6d4fd22b20465ccc0f7354476588e8df7c9ca0e0 |
| upload-artifact v7.0.2 | cf430e030ddbb5b0abf93d22962f4752f3646cd9 |

Official repositories' Git tag refs resolve directly to these commits; GitHub
commit verification is true for each. Their action.yml declares node24. Inputs
used by this workflow remain available. Upload keeps default archive=true, existing
artifact names/paths and retention; no raw-file artifact migration is introduced.
Checkout still uses persist-credentials=false. Checkout requires runner >=2.329.0;
setup-python requires >=2.327.1. Future private runner must meet the stricter floor.
Sources: [checkout](https://github.com/actions/checkout/releases/tag/v7.0.1),
[Python](https://github.com/actions/setup-python/releases/tag/v7.1.0),
[upload](https://github.com/actions/upload-artifact/releases/tag/v7.0.2).
Download-artifact remains at its existing pin in skipped publish/deploy jobs; review
its runtime/compatibility separately before enabling those jobs. This correction
does not certify the still-unimplemented private deployment connection.

## Validation

- Vote and Worker final-target Docker builds: PASS. Result unchanged/reused.
- All three actual musl versions: 1.2.6-r3; non-root users preserved.
- Trivy 0.75.0 DB update check: PASS; database UpdatedAt 2026-10-26T01:20:01.38093772Z,
  downloaded 2026-10-26T03:13:17.950783334Z. Not yet due for another DB download.
- Fresh scans of all three exact image IDs, **all severities including UNKNOWN**:
  zero reported findings, no missing-details or other WARN lines; target CVE absent.
  No ignores, suppression or logging weakening. Scan-tool success is not a guarantee
  against undisclosed flaws. Current DB was reused consistently for all scans.
- Nine-check disposable Docker application acceptance: PASS; non-root/read-only,
  compressed-body regression, live Socket.IO scores, dependency readiness,
  persistence/recovery and bounded shutdown. Old-image package rejection: PASS.
- Eleven CI guard tests, Actionlint, ShellCheck, Helm strict lint/render/schema/
  negative/determinism checks, Compose configuration and whitespace checks: PASS.
- Existing unrelated working changes remain excluded. Only seven focused files
  staged; Gitleaks 8.30.1 full staged snapshot scan PASS with no leaks.

Evidence stays outside Git under `C:\Users\akord\Desktop\devops-capstone-remediation`:
`musl-{vote,worker}-build.log`, `musl-images.json`, `musl-acceptance.json`,
`musl-negative-regression.log`, `musl-trivy-{vote,result,worker}.{json,log}` and
`musl-trivy-update.log`. No image/archive/report artifacts added to the PR.

## Next gate

Request approval to push only the resulting correction commit to the existing
feature branch, without force, and inspect its new hosted run. Keep PR draft,
publication/deployment opt-ins absent and no merge. Hosted image builds and tests
must independently pass before merge readiness is reconsidered. If CI fails,
prepare a local correction and request approval before another push. This local
commit cannot alter the running application. Do not revert to the old vulnerable
images as a release recovery strategy; preserve the current production baseline
until a separately reviewed deployment is authorized.
