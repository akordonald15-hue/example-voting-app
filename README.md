# TS Academy DevOps — Voting App and Robot Shop

**Submission entry point:** [two-project evidence package](submission/README.md).

- **Capstone 1:** [Voting App delivery and limitations](submission/capstone1.md) — Compose, hardening, Terraform, AWS K3s/Helm, hosted CI/Trivy/GHCR and isolated local rollback evidence.
- **Capstone 2:** [Robot Shop observability](submission/capstone2.md) — local kind checkout/load, RED dashboard queries, logs, traces, SLO and local incident evidence. **Robot Shop was not deployed to AWS.**
- [Requirement matrix](submission/requirement-matrix.md) · [evidence index](submission/evidence-index.md) · [architecture diagrams](submission/architecture.md) · [reproduction](submission/reproduction.md).

The AWS Voting App and PostgreSQL are preserved. A separate tainted worker was provisioned/joined, but Robot Shop AWS deployment remains incomplete. Web/Cart GHCR publication succeeded;Catalogue DNS failure blocked remaining publication. No automatic production deployment, Terraform destroy/recreate, full production rollback, Slack delivery or fresh complete Robot Shop Trivy scan is claimed.

New submission documents are local until separately approved for commit/push. See [safe submission checklist](submission/git-and-submission.md). Do not run infrastructure, deployment, recovery or volume-deletion commands to manufacture missing evidence.

## Source and attribution

Voting application based on [Docker Samples Example Voting App](https://github.com/dockersamples/example-voting-app). Robot Shop based on [instana/robot-shop](https://github.com/instana/robot-shop), with [snapshot provenance](capstone2/upstream-receipt.json). Existing licenses are retained.

Source entry points: [Compose](docker-compose.yml),[Vote](vote/),[Result](result/),[Worker](worker/),[Voting Helm chart](helm/voting-app/),[Terraform](terraform/),[Robot Shop](capstone2/).
