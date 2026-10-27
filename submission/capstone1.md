# Capstone 1 — Voting App delivery

**Submission summary:** Hardened Docker applications, Compose rehearsal, Terraform-managed AWS K3s, hosted acceptance/security CI, GHCR publication and an owner-confirmed functioning Helm deployment. Manual Helm rollback was demonstrated only with an isolated local Vote fixture.

## Verified and recorded scope

- Compose voting/live score updates and hardening were previously recorded locally; see the [sanitized historical report extracts](evidence/capstone1-local-reports.md). No rerun was performed for closeout.
- Runtime Dockerfiles: [Vote](../vote/Dockerfile), [Result](../result/Dockerfile), [Worker](../worker/Dockerfile). Multi-stage/final targets, non-root configuration and runtime health behavior are reviewable source, not a fresh security scan.
- [Terraform source](../terraform/) provisions the control-plane infrastructure; [separate worker root](../terraform-worker/) isolates the later worker. Provisioning occurred; source comments saying preparation-only are historical. Raw plans/state/tfvars/apply logs are private and excluded. [Infrastructure evidence scope](evidence/infrastructure-status.json).
- AWS application state is **owner-confirmed**, not newly queried: Helm revision 2 deployed, five Ready workloads/zero restarts at the accepted checkpoint, preserved bound PostgreSQL PVC, private browser vote/result functioning. No fresh live output/screenshots were supplied for this closeout.
- Hosted CI recorded13 guard tests,9 acceptance checks and3 all-severity Trivy scans. [Recorded publication run attempt2](https://github.com/akordonald15-hue/example-voting-app/actions/runs/40294083665/attempts/2); [workflow source](../.github/workflows/capstone.yaml). Preserve/download its real artifacts if available; this packaging pass did not rerun or redownload hosted CI.
- Published source bd9dfa3a2cf3bf27c893a3a7a64b81e8b7c00115 and immutable image refs are in [publication evidence](evidence/capstone1-published-images.json). Publication does not prove those exact images are running in AWS.
- [Isolated rollback evidence and exact chart](../docs/rollback-evidence/README.md): healthy revision 1, intentional failed readiness revision 2, manual rollback to deployed revision 3. Vote-only local fixture; not full-stack/AWS/PostgreSQL rollback.

## Incomplete and limitations

Automatic push-to-production delivery was not demonstrated; successful publication run skipped deployment. Public repository runner labels alone are not a secure isolation boundary. Separate trusted promotion/RBAC/environment/pull-access controls remain necessary; no activation is authorized.

Terraform destroy/recreate was **not demonstrated**. Do not destroy live infrastructure to fill this gap. The local-path PostgreSQL data is node-bound; Helm rollback cannot restore database contents. Full production application rollback/database restore is not demonstrated. Earlier failed/recovered release notes are historical and must never be rerun blindly.

Recorded clean scans apply only to their image/time/database. Earlier legacy image scans had findings, and no current vulnerability-free claim is made. Existing architecture, reproduction, evidence and matrix are linked from [submission home](README.md).

**Reviewer starting points:** this guide, hosted run, Dockerfiles/chart/Terraform source, rollback history, and explicit missing owner live screenshots/status receipts. Keep credentials and private kubeconfig out of the submission.
