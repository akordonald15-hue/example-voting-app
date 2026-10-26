The Voting App needs reproducible runtime images and release checks before its
first verified GitHub deployment. This change pins non-root runtime images and
dependencies, adds readiness/recovery handling and a disposable five-component
test, and introduces a digest-aware Helm chart with external Secret references
and retained PostgreSQL storage.

The replacement workflow verifies PRs on hosted runners. Publishing and deployment
require separate main-push opt-ins, currently absent. Publishing reuses tested
image bytes with full commit-SHA tags; deployment permits only application-image
changes and checks the approved current PostgreSQL claim identity. No production
resource changes, recovery tooling, Capstone 2 artifacts or Terraform changes are
included. No remote runner is registered by this PR.

Validation: 11 CI guard tests, eight exact-image integration checks, Actionlint,
ShellCheck, Helm lint/render/schema checks and Compose configuration passed.
Staged secret scan found no leaks. Fresh Trivy 0.75.0 scans reported zero HIGH
and CRITICAL for Vote, Result and Worker. Vote/Worker emitted an unresolved
missing-details database warning for CVE-2026-107891; retain and recheck it before
merge/release. See `docs/capstone1-pr-readiness.md` for scope, evidence and gates.

Hosted CI is not yet proven. Keep publication/deployment opt-ins disabled during
review; merge, registry publication and production deployment require separate
approval. The live rollback and isolated Terraform recreation demonstrations
remain outstanding. This PR does not claim final capstone completion.
