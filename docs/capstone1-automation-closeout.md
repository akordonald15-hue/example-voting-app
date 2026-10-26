# Capstone1 automation closeout — local verification

October26,2026. **GO for local review; NO-GO for production activation.**
This checks implementation and adversarial fixtures, not a live runner, registry
credential or production API. No variables/settings were changed; no AWS or
GitHub mutation, commit, push or deployment occurred.

## Verified now

| Check | Actual result |
|---|---|
| Python guard suite |30 tests passed:13 original release/render/security,10 promotion,7 pull-validation |
| Actionlint1.7.12, public source workflow |PASS with ShellCheck separately disabled in Actionlint invocation |
| Actionlint1.7.12, private promotion proposal |PASS using its explicit proposed runner-label configuration |
| ShellCheck0.11.0 |PASS for `scripts/ci-deploy.sh` and proposed promotion shell wrapper |
| Helm4.3.1 default chart harness |PASS: four release names,17 resources,5 workloads,4 ClusterIP services,7 policies; negative schemas, digest override and long-name collision tests |
| Helm harness with original published values overlay |Same positive and negative checks passed; digest overlay does not accidentally defeat the invalid-tag negative case |

Executed commands (Docker tools used existing images with network disabled and
repository mounted read-only):

```text
python -B -m unittest discover -s scripts -p 'test_ci_*.py' -v
actionlint -shellcheck= .github/workflows/capstone.yaml
actionlint -shellcheck= -config-file <private-proposal-config> <private-proposal-workflow>
shellcheck scripts/ci-deploy.sh <private-proposal-wrapper>
python -B scripts/validate-helm.py --helm <local-helm>
python -B scripts/validate-helm.py --helm <local-helm> --values <original-private-release-values>
```

The private release values were consumed from the retained original publication
artifact outside Git, never copied into this public submission document. No
private deployment bundle is to be staged as part of this closeout report.

## Current public workflow boundary

[capstone.yaml](../.github/workflows/capstone.yaml) runs verification on main push
and PR. Publication requires main **push**, successful verify and
`CAPSTONE_PUBLISH_ENABLED == 'true'`. Deployment requires successful publish,
main **push**, `CAPSTONE_DEPLOY_ENABLED == 'true'`, the `capstone-production`
environment and self-hosted Linux runner label `capstone-private-deploy`.
These are independent opt-in expressions, not evidence the variables are currently
absent remotely. No remote variable query was performed in this local test.

The successful historical publication run did not demonstrate automatic production
deployment. The public workflow's runner label alone is **not** an isolation
boundary: an untrusted workflow can request a matching public-repository runner.
Do not register a production-capable runner there to satisfy the rubric quickly.

The local feature workflow retains an older download-artifact pin than the
separately reviewed Node24 correction on published main. Actionlint passing does
not establish runtime currency. Reconcile that exact workflow against approved
remote main before any activation; do not overwrite a remote correction from a
stale feature checkout. No pin was changed in this closeout.

## Private promotion proposal: implemented safeguards

The local proposal is a separately controlled **manual** artifact-promotion path,
not installed infrastructure and not automatic deployment for future commits.
It permits only named-owner dispatch on private main with an exact release
confirmation, independent enable gate and production environment approval.
It fixes source commit `bd9dfa3a2cf3bf27c893a3a7a64b81e8b7c00115`, original
run40294083665 attempt2, artifact12637369477 and three published digests.

Tests rejected wrong source/attempt, expired or substituted artifact, modified
values, partial/failed/mixed job receipts, wrong repositories/digests, invalid
manifest/platform/runtime identity and missing registry evidence. No build or
push occurs in the promotion workflow. Registry verification uses private
temporary auth storage and fails on errors rather than inventing a clean receipt.

The wrapper requires baseline deployed status, exactly five Ready application
Pods, reviewed release/artifact identity and an explicit kubeconfig path. It
compares stored Helm desired resources against the proposed render with the
image-only guard; checks the PVC before/after; compares Redis/PostgreSQL Pod
identity/image/restarts; checks actual runtime image identity against registry
receipts; and stops without automatic retry/rollback on uncertain Helm outcome.
The successful path still needs an operator browser acceptance gate.

Pull-validation fixture tests verify fixed utility-only manifests, complete pull
evidence, owner/node/entrypoint/policy validation, UID-precondition deletion,
restricted cleanup and no retry after uncertain creation. These are offline
tests, not proof the three live pull Jobs ran.

## Remaining production gates

1. **Trust boundary:** approve/create a private deployment repository or enforceable
   selected-workflow runner group. Restrict trusted writers and protect workflow,
   policy and main. A private-repository-scoped ephemeral runner must not also
   accept public source jobs; no production-host runner or Docker socket.
2. **Approval enforcement:** verify the actual GitHub plan supports required
   reviewers/protected-environment restrictions for that private repository.
   Environment naming is not enforcement. A sole owner cannot supply independent
   peer review; document any explicitly accepted solo-operator limitation.
3. **Network and credentials:** approved private TLS-verified Kubernetes path,
   current supported runner/tools, source Actions read permission, scoped GHCR
   read permission and namespace Kubernetes authorization. No credentials in Git,
   command arguments or artifacts. No public Kubernetes ingress.
4. **RBAC residual risk:** Helm release Secret read/list can reveal database/pull
   credentials in the same namespace; create cannot be restricted to resourceNames
   by ordinary RBAC. Review a storage/admission design or explicitly accept this
   residual risk. Do not label broad Secret access least privilege.
5. **Live release preflight:** independently authenticated GHCR manifests and
   platform selection, original artifact availability/hash, unchanged healthy
   production/PVC binding, complete live drift/defaulting review and a bounded
   approved release window. Protect PVC UID
   `44527b3d-1dd6-429c-9dca-14afc31f1552`. No database/Secret rotation or repair.
6. **Actual automation evidence:** successful gated runner execution, deployed
   Helm status, preserved backend/PVC identities, expected runtime digests and
   browser acceptance. Until then submit automatic production deployment as
   **not demonstrated**, regardless of green local tests.

For a true push-to-deploy requirement, design an approved trusted promotion
handoff of each successful immutable source artifact into that private boundary,
with provenance validation and required approval. Never blindly dispatch arbitrary
repository/SHA/artifact inputs. The current frozen manual proposal intentionally
does not implement that generalized future-release mechanism.

No new controller/script correction was necessary for these passing offline
tests. The outstanding work is trusted runtime setup, live evidence and approval,
not another production upgrade or a repeat of already completed image builds.

The focused closeout commit also includes the previously prepared Helm harness correction: clear the digest only in the invalid-tag negative case. Otherwise a valid published digest legitimately overrides the invalid tag, producing a misleading test failure. Positive digest-overlay and negative schema tests passed with the corrected harness.
