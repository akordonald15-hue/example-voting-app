# Safe Git review and submission checklist

## Current state and boundaries

Repository origin: https://github.com/akordonald15-hue/example-voting-app.git
Current branch: feature/capstone2-aws-preparation. Base HEAD:19a99bba321da9d90c3270bb8a9198e1756c5860. No commit/push performed for this closeout.

The base has2 local commits beyond the last fetched origin/feature/capstone1-ci-release-readiness ref: c403670 and19a99bb. A future push would include these ancestors: review them too. No main merge or force push. Remote refs are locally cached, not a fresh network verification.

Unrelated seed-data/Dockerfile modification and numerous untracked private recovery/release/IAM/apply artifacts are deliberately NOT selected. Never stage the entire workspace. Private state/tfvars/kubeconfig/tokens, private promotion bundles, raw infrastructure receipts, network-context dumps and binaries are excluded. Existing upstream default demo passwords in tracked source are not production credential evidence; review scanner findings before approving upload.

[Explicit proposed paths](selected-files.txt) is the allowlist. It includes current guides, relevant AWS overlays/chart placement changes and selected sanitized evidence needed for linked reproduction. Existing tracked local-runtime evidence is inherited from reviewed ancestor commits. It excludes publication/retry controllers and private network/environment diagnostics.

## Commands to review now (read-only)

```powershell
git branch --show-current
git remote get-url origin
git status --short
git log --oneline origin/feature/capstone1-ci-release-readiness..HEAD
Get-Content submission/selected-files.txt
git diff --check
git diff --stat
```

## ONLY after separate staging/commit approval

```powershell
git add --pathspec-from-file=submission/selected-files.txt
git diff --cached --name-only
git diff --cached --check
git diff --cached --stat
git diff --cached
```

Compare staged paths exactly with the allowlist and review all content/security findings. If any unexpected or sensitive path is staged, stop; do not commit it. Then, only with explicit commit approval:

```powershell
git commit -m "Prepare honest evidence and submission guides for both capstones"
git rev-parse HEAD
```

## ONLY after separate push approval

Reconfirm branch/origin, review all outgoing ancestor commits and check no unreviewed changes are staged. Push only the reviewed feature branch:

```powershell
git push -u origin HEAD:refs/heads/feature/capstone2-aws-preparation
git ls-remote origin refs/heads/feature/capstone2-aws-preparation
```

Require remote SHAequals approved local SHA. No push was run during closeout. Proposed submission URLs AFTER approved upload:

- https://github.com/akordonald15-hue/example-voting-app/blob/feature/capstone2-aws-preparation/submission/capstone1.md
- https://github.com/akordonald15-hue/example-voting-app/blob/feature/capstone2-aws-preparation/submission/capstone2.md

Prefer replacing the branch segment with the final full commit SHAfor permanent evidence. Verify reviewer access and every link after upload; newly created files are not yet known accessible on GitHub.

## Final submission checklist

- [ ] Review selected files, secret scan, link audit and both local ancestor commits.
- [ ] Obtain explicit commit and push approval; record/upload the exact reviewed SHA.
- [ ] Open both submitted guides on GitHub as the reviewer would.
- [ ] Attach genuine redacted AWS browser/Helm/node/PVC/worker evidence if the owner has it; otherwise retain the missing-evidence disclosure.
- [ ] Verify hosted run/artifact access/retention; retain genuine CI acceptance/security receipts if available.
- [ ] Keep65/70 and 124/126failures and unsuccessful Job outcomes alongside151/151browser-profile success.
- [ ] State Robot Shop was local kind only; AWS worker is not AWS Robot Shop deployment.
- [ ] State Web/Cart published, three pending, DNS instability blocked continuation.
- [ ] State Slack delivery, fresh full Robot Shop Trivy, automatic production deploy, Terraform destroy/recreate and full production rollback incomplete.
- [ ] Include dashboard JSON/query responses, logs, traces, local incident and matrix;do not invent screenshots.
- [ ] Preserve production/database state. Submission does not authorize cleanup, publication or deployment.

Security audit is bounded: [report](security-review.json). Internal-link checks: [report](link-review.json). No guarantee that historic Git history or expired remote artifacts are clean/available is implied.
