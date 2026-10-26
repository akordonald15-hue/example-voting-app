# Helm Rollback Demonstration

Date: October 26, 2026

## Environment

- Cluster: kind-capstone-rollback-lab
- Kubernetes: v1.35.0
- Namespace: rollback-lab
- Helm release: rollback-lab
- Container: locally built, hardened Voting App Vote image
- Scope: isolated local rollback fixture; not the full production Voting App

## Test Procedure

1. Installed Helm revision 1 with readiness endpoint `/health`.
2. Verified the deployment was healthy and its pod was Ready.
3. Upgraded to revision 2 using `/intentional-missing-rollback-probe`.
4. Kubernetes returned HTTP 404 for the new readiness probe.
5. Helm upgrade timed out with exit code 1.
6. Executed `helm rollback rollback-lab 1`.
7. Verified revision 3 was deployed, the workload recovered, and `/health` was restored.

## Results

| Revision | Status | Result |
| --- | --- | --- |
| 1 | Superseded | Healthy baseline |
| 2 | Failed | Deliberate readiness failure |
| 3 | Deployed | Successful rollback to revision 1 |

The recovered deployment successfully rolled out and the original pod
was Ready (1/1) with zero restarts.

## Evidence

- `history-after-failure.txt`
- `pods-after-failure.txt`
- `events-after-failure.txt`
- `history-after-rollback.txt`
- `pods-after-rollback.txt`
- `values-after-rollback.txt`
- `final-helm-history.txt`
- `final-pod-status.txt`
- `final-restored-values.txt`
- `chart/` — exact Helm fixture used

## Limitations

This demonstration validates Helm's manual rollback mechanism in a
disposable local Kubernetes cluster using the Voting App Vote image.

It does not demonstrate a rollback of the complete Voting App stack,
a production AWS rollback, or recovery of a PostgreSQL persistent volume.
The AWS production release was not modified during this exercise.
