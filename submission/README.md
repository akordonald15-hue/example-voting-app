# TS Academy DevOps capstone submission

Submit these two project guides with the exact reviewed Git commit. This is an honest evidence package, not a claim that every rubric item passed.

- [Capstone 1 — Voting App](capstone1.md)
- [Capstone 2 — Robot Shop](capstone2.md)
- [Requirement-to-evidence index](evidence-index.md)
- [Completed/partial/incomplete matrix](requirement-matrix.md)
- [Architecture diagrams](architecture.md)
- [Reproduction and safety boundaries](reproduction.md)
- [Incident and publication postmortems](incidents.md)
- [Safe Git review and submission checklist](git-and-submission.md)

**Scope:** Voting App ran on AWS K3s; Robot Shop demonstrations ran locally in kind. An AWS worker was provisioned/joined (join/health owner-confirmed), but Robot Shop was never deployed to AWS. Web and Cart were published to GHCR; Catalogue publication failed due Docker DNS and Payment/Loadgen were not attempted. No further publication/deployment is part of submission preparation.

No successful Slack delivery, fresh complete Robot Shop Trivy scan, automatic production deployment, Terraform destroy/recreate, or full production rollback is claimed. Existing failure evidence is retained. New documents remain local until a separately approved commit/push; proposed GitHub URLs are not evidence they already exist remotely. No screenshots are fabricated.
