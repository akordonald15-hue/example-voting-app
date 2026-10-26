# Capstone 1 PR readiness — 2026-10-26

**GO for a review-only PR after explicit publication approval; NO-GO for merge,
image publication or deployment.** Local branch: `feature/capstone1-ci-release-readiness`.
No remote writes or production changes performed.

## Scope and inventory

Initial full working-tree inventory: 211 pending paths, with path/status/hash receipt
outside Git at `C:\Users\akord\Desktop\devops-capstone-remediation\pr-working-tree-inventory.json`.
46 paths selected: 16 application/Compose paths and 30 chart/CI/release-validation
paths (including three removed upstream publishing workflows). This report and
PR description add two documentation paths. Exact proposed inventory is obtained
with `git diff --name-status main...HEAD`; no blanket staging.

Excluded: 70 Capstone 2 source paths; 66 separate documentation/infrastructure
paths; 14 generated/evidence paths; 15 historical tooling paths. Terraform source
is validated but intentionally excluded from this application/CI PR. Seed profile
changes, root README changes and historical recovery source remain local. No
existing uncommitted work was discarded. The working tree is intentionally dirty
outside this bounded PR; commits, not `git add .`, define publication scope.

Ignored sensitive/generated material includes Terraform state/backups, plans and
plan transcripts, provider cache and Python caches. Apply logs and release tarballs
were untracked but not necessarily ignored: exclusion was explicit. Filename
checks found no eligible `.env`, private key or kubeconfig candidates. Never
interpret that as proof ignored state is safe to publish.

Gitleaks 8.30.1, network disabled, staged full-repository snapshot: exit 0, no leaks.
Full eligible working-tree snapshot: one redacted generic-api-key finding at
`docs/final-predeployment-review.md:55`, reviewed IAM permission/variable example,
not a credential; excluded from PR. No ignore rule added. Ignored state/cache files
were not copied into secret-scan snapshots. Reports stay outside Git; no secret
values or raw diagnostics are included in this report.

## Workflow audit

- Only `push` to main and `pull_request` targeting main. No schedules, dispatch,
  `pull_request_target`, workflow_run or reusable-workflow calls. All three old
  publishing workflows are removed in the same PR.
- Default/verify permissions contents:read; checkout credentials not persisted.
  Verify runs on hosted Ubuntu, builds final targets, runs eleven guard tests,
  disposable five-component acceptance and three vulnerability scans.
- Trivy/action versions pinned; HIGH/CRITICAL including unfixed block release.
  A scan error fails closed. Subsequent scan steps may be skipped after a failed
  preceding step; this cannot enable publication because publish needs verify.
- Tested Docker archive is passed to publishing, no independent image rebuild.
  Publisher alone receives packages:write and requires main push plus opt-in.
  Full commit-SHA tags and digest-only runtime references are generated.
- Deploy needs publish, main push and separate opt-in, protected environment and
  dedicated private runner. PRs cannot select this runner through these jobs.
  Full render comparison permits only three application-image changes; current
  recovered PVC UID/binding guard and readiness receipts protect deployment.
- No install/force/automatic rollback, Secret update, storage deletion or Terraform
  execution. Failure/uncertain upgrade stops; bounded nonsecret evidence retained.
- Exact action pins do not pin hosted runner OS contents, PyPI transitive supply
  chain or vulnerability DB. Hosted execution remains necessary evidence.

GitHub live read-only checks: repository-owned variables list empty (`gh variable
list` and API agree); environments list empty. Owner type User, so no organization
variable inheritance. Both opt-ins **absent, not enabled**. Recheck immediately
before publication; this is not a promise against later administrator edits.
Private runner/environment/access design remains unimplemented and unapproved.

## Fresh local validation

| Check | Result |
|---|---|
| CI guard suite | 11 PASS |
| Actionlint 1.7.12 / ShellCheck 0.11.0 | PASS |
| Helm strict lint/render/schema/negative/determinism checks | PASS; 17 resources, five workloads, seven policies |
| Terraform fmt/validate | PASS; no init/apply/plan/destroy or source change |
| Docker Compose configuration | PASS |
| Exact-image disposable integration | PASS, eight checks; readiness, compressed-body regression, Socket.IO, voting/cookie update, non-root/read-only controls, persistence/recovery and clean shutdown |
| Staged diff whitespace / secret scan | PASS |
| Trivy 0.75.0 database download | PASS from mirror.gcr.io/aquasec/trivy-db:2 |
| Vote / Result / Worker HIGH, CRITICAL | 0/0 each; each scan exit 0 |

DB UpdatedAt `2026-10-26T01:20:01.38093772Z`, DownloadedAt
`2026-10-26T03:13:17.950783334Z`. Per-image scans reused that freshly downloaded DB
with `--skip-db-update` to avoid another download; no stale database or vulnerability
ignore used. **Unresolved warning:** Vote and Worker report missing vulnerability
details for `CVE-2026-107891` (Trivy says it may be rejected). No rejection/fix is
asserted. Reported zeros are subject to that database limitation; retain warnings
and recheck on hosted CI/new DB before approving merge or release.

Reports: outside Git under `C:\Users\akord\Desktop\devops-capstone-remediation`,
`pr-acceptance.json`, `pr-trivy-{vote,result,worker}.{json,log}`,
`pr-trivy-update.log`, `pr-staged-gitleaks.{json,log}`, `pr-full-gitleaks.{json,log}`.
Exact image IDs remain in the acceptance report; existing production was not tested
or changed by this local rehearsal. Legacy PhantomJS test is superseded for this
candidate by the shipped Socket.IO browser-client regression, not counted as run.

## Approval and recovery

After reviewing commits and rechecking opt-ins, approve only branch push and draft
PR creation. Commands from repository root (NOT executed):

```powershell
git log --oneline main..HEAD
git diff --check main...HEAD
git diff --name-status main...HEAD
gh variable list --repo akordonald15-hue/example-voting-app --json name,value
git push --set-upstream origin feature/capstone1-ci-release-readiness
gh pr create --repo akordonald15-hue/example-voting-app --base main --head feature/capstone1-ci-release-readiness --draft --title "Harden Voting App and add gated digest-based release CI" --body-file docs/capstone1-pr-description.md
```

PR triggers hosted tests/builds/scans and artifact uploads only; no production
rollout. Risk: source disclosure and CI/artifact quota. Review scan warning and
actual hosted result before merge. Recovery: close PR/correct with a follow-up
commit; never assume deleting Git history revokes a leaked credential. No force
push or destructive cleanup is needed. Local rollback: switch back to main only
when Git can preserve the remaining uncommitted work; do not reset/clean it.

Merge, GHCR opt-in/publication, private runner/RBAC, deployment activation, live
rollback exercise and isolated Terraform recreation each require separate approval.
Production PostgreSQL/PVC is outside this PR's execution scope. Deployment later
can interrupt the three Recreate app Deployments; no database rollback is implied.
