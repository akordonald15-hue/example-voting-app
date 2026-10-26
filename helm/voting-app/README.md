# Voting App Helm chart — Stage 5 local preparation

One chart and one `values.yaml` describe four Deployments (vote, result, worker, Redis), a PostgreSQL StatefulSet with retained PVC, four ClusterIP Services, a ConfigMap and seven NetworkPolicies. No seed service, public ingress, NodePort, cloud load balancer, namespace or Secret is created. Kubernetes deployment is **not authorized** by this README.

## Deployment readiness

Local lint/render/build/regression evidence is recorded in [the Stage 5 report](../../docs/stage-5-helm-preparation.md). This is **not yet a deployable release**: the three modified application images have only been built locally. `stage5-unpublished` tags deliberately identify unavailable release placeholders; no GHCR publication or remote image availability is claimed. Existing upstream application images do not contain these source changes and must not be substituted silently.

Before a separately authorized install:

1. Publish the three modified images through a later approved build/release flow, using linux/amd64 for the current node. Use a reviewed source commit SHA tag and preferably registry digest. No tag should imply that today's uncommitted changes are the original baseline commit. Record image provenance and scanning findings. Do not publish from the inherited workflows until their Docker Hub/upstream GHCR destinations and mutable reusable-action reference have been reviewed in Stage 6.
2. Edit only the corresponding image fields in the single values file, then lint/render/review again. Every image supports `repository`, version `tag`, optional `sha256:` digest and `pullPolicy`; digest takes precedence. `latest` tags without a digest are rejected. Redis/PostgreSQL defaults retain the already-reviewed digest pins and versions; do not change runtimes merely to resolve a warning.
3. Privately create the approved existing database Secret in the intended namespace and configure its name/key in values (defaults `voting-app-db`, `password`). Never put a password into values, a Helm `--set` argument, a command argument, Git or the chat. A future administrator can use `kubectl create secret generic ... --from-file=password=<protected-local-password-file>` after explicit authorization; the file must contain the intended password bytes without an accidental newline. No Secret was created during local validation.
4. Public GHCR packages need no pull Secret; private packages require a separately approved namespace-local registry Secret and `imagePullSecrets: [{name: ...}]`. Avoid publishing tokens in values; specify only Secret names. Pod service-account API tokens are disabled.
5. Confirm node Ready/system pods healthy, local-path StorageClass available/default behavior, CoreDNS pod labels `k8s-app=kube-dns`, K3s network-policy enforcement enabled, allocatable/headroom sufficient, intended namespace clean, and no existing conflicting release/PVC/data. These are future read-only cluster checks, not checks performed here. The owner reports K3s v1.36.5+k3s1 Ready and service running but autostart disabled; do not assume recovery after reboot or enable it in this stage.
6. Obtain explicit approval for the chart, values, exact published image digests, namespace, Secret/PVC creation and deployment command. No cloud/network/IAM changes are required by this chart.

## Runtime contracts and small source changes

| Component | Container port | Runtime inputs | Dependency/readiness |
| --- | --- | --- | --- |
| vote | 8080 | REDIS_HOST, OPTION_A/B | New `/health/live` and Redis-backed `/health/ready` |
| result | 8080 | PORT, PGHOST/PGPORT/PGUSER/PGDATABASE, Secret PGPASSWORD | New health routes; readiness queries the worker-created votes table |
| worker | None | Same PG inputs, REDIS_HOST; WORKER_HEARTBEAT_PATH | Startup waits for heartbeat; readiness checks age of completed work/dependency loop |
| Redis | 6379 | Bounded maxmemory 64mb, noeviction | redis-cli must return PONG |
| PostgreSQL | 5432 | POSTGRES_USER/DB, Secret POSTGRES_PASSWORD, PGDATA | pg_isready with generous initialization window |

The ConfigMap derives database/Redis DNS from the Helm release name. No Compose hostname is baked into the rendered application configuration. Legacy environment defaults are retained in source for existing Compose behavior. Kubernetes always supplies the explicit configuration and password Secret. Passwords are passed as separate PG fields/Npgsql builder fields, so delimiter characters are not interpolated into connection URLs.

Vote uses the existing final image's gunicorn binary with 2 workers/2 threads on high port 8080; result uses `node server.js` without nodemon/debug port. Worker records a heartbeat only after its processing loop completes and dependencies have responded. A small reconnect fix rebinds its keep-alive command after opening a new database connection. Result's missing Node path import was corrected while preserving its `/` page behavior. New routes do not publish dependency error details/passwords.

No init containers enforce startup order. Services/DNS exist independently; source retry loops, process restart and readiness handle asynchronous availability. HTTP startup/liveness check local process health; readiness checks dependencies, so database downtime does not intentionally restart the frontend. Worker deliberately has no liveness probe tied to dependencies; readiness becoming false indicates stale work, while process exit causes a normal Kubernetes restart. Its five-minute startup allowance can restart a worker that never reaches its first successful loop. A stalled-but-alive worker after startup is an acknowledged monitoring limitation, not a complete processing SLO.

## Resource budget

| Component | CPU request / limit | RAM request / limit |
| --- | --- | --- |
| vote | 100m / 500m | 128Mi / 256Mi |
| result | 100m / 500m | 96Mi / 192Mi |
| worker | 100m / 500m | 128Mi / 256Mi |
| Redis | 50m / 250m | 64Mi / 128Mi |
| PostgreSQL | 100m / 500m | 192Mi / 384Mi |
| Total | 450m / 2250m | 608Mi / 1216Mi |

Requests reserve scheduling capacity; limits bound each container, not node-wide usage. CPU limits sum above the two cores to allow contention-based bursting, not simultaneous guaranteed CPU. RAM limits leave nominal room for K3s, existing system pods, page cache and growth on a 4-GiB node, but only live measurements can establish headroom. The owner last reported about 2.8 GiB available; it was not remeasured. PostgreSQL max_connections=30/shared_buffers=64MB and bounded Redis queue memory support this starting lab budget. Watch OOMKills, pending pods, runtime memory, disk/ephemeral storage and T3 CPU-credit throttling before tuning. This is not Robot Shop/observability sizing.

All replicas are one and Deployments use Recreate to avoid temporary double-pod memory and duplicate workers during a lab release; upgrades have downtime. No HPA or disruption budget pretending to provide single-node availability is included.

## Persistence and lifecycle

PostgreSQL uses `/var/lib/postgresql/data/pgdata` on a configurable 2Gi local-path RWO claim. UID/GID 70 and fsGroup 70 provide initialization/data access; writable emptyDirs cover `/var/run/postgresql` and `/tmp`. Redis runs UID 999 with writable emptyDir `/data`; applications run UID 1000 with writable `/tmp`. All containers drop capabilities, forbid privilege escalation and use read-only root filesystems with RuntimeDefault seccomp. These UIDs were checked against the pinned images in disposable local containers; a custom image can require a reviewed UID change.

StatefulSet claim retention is Retain on scale/delete. Uninstalling the release does not deliberately delete its generated database claim; inspect it before reinstall. Reusing the same release/claim preserves data only if the node/disk and credentials remain compatible. local-path does not provide replicas, shared cross-node storage, managed backups or data recovery from EC2/root-disk destruction. Deleting a PVC may trigger the provisioner's Delete reclaim behavior and remove backing files. Snapshot/backup/restore requires a separately approved plan.

Do not resize an existing StatefulSet claim by assuming editing `storageSize` will work; volumeClaimTemplates are generally immutable and local-path has limitations. Do not change database name/user/storage settings on an initialized volume without a reviewed migration. Changing the Secret does not change an existing database's password automatically; env values do not hot-reload, and rotation needs coordinated database/application changes. No secret data is included in Helm history by this chart, but user-supplied secret values/arguments could defeat that safety.

Redis is explicitly volatile: restart loses queued/unprocessed votes. The worker's pop-then-write algorithm is not transactional/exactly-once; a crash between operations can lose a vote. PostgreSQL persists processed votes. These are inherited application limitations, not fixed by the chart. The app uses a browser cookie, not a strong voter identity. DB bootstrap user has initialization/superuser privileges; scoped DB roles and Redis authentication remain later hardening work. Chart security is not a claim of internet-production readiness.

## Private access — future commands only

After separate approval and install, use the approved SSM Kubernetes API tunnel (local 16443 to node 6443) and a protected kubeconfig whose server points to that tunnel. Do not print/copy it into Git. This chart does not create the tunnel or fetch credentials.

For release `capstone` and namespace `voting-app`, from separate local terminals:

```powershell
kubectl --kubeconfig <protected-path> -n voting-app port-forward service/capstone-voting-app-vote 18080:80 --address 127.0.0.1
kubectl --kubeconfig <protected-path> -n voting-app port-forward service/capstone-voting-app-result 18081:80 --address 127.0.0.1
```

Then browse http://127.0.0.1:18080 and http://127.0.0.1:18081. These do not collide with Compose ports 8080/8081. Port-forwarding is expected to work through the node/kubelet path rather than opening pod ingress; verify on the actual K3s CNI after deployment. NetworkPolicies default-deny chart pod ingress/egress, allowing only DNS plus vote/worker→Redis and worker/result→PostgreSQL in the same release/namespace. No public frontend Service or network-policy exception is included. A later ingress/HTTPS strategy needs independent approval, network policy review and a cost review.

## Local validation (no cluster)

```powershell
python scripts/validate-helm.py --helm <path-to-helm.exe>
docker build --target final -t example-voting-app-vote:stage5-local vote
docker build -t example-voting-app-result:stage5-local result
docker build -t example-voting-app-worker:stage5-local worker
python scripts/test-stage5-local.py
```

PyYAML is needed for these local validation scripts; already available in this environment. They do not install tools. The integration test intentionally creates its own disposable LOCAL Docker network, containers and volume with test-only generated credentials; it removes only those resources. It never accesses the Compose DB or Kubernetes/AWS. It checks dependency outage/readiness, custom DNS and credentials, actual votes and Socket.IO, rootless/read-only execution and DB persistence after its own test database restart. It does not prove Kubernetes scheduling, network policies, PVC fsGroup behavior, GHCR pulls, browser interaction, or rollback correctness. No cluster API/schema validation or cluster installation has been performed.

Never paste credentials into testing output. Keep future Helm release operations independently authorized. A Helm rollback does not roll back database contents/schema or restore deleted storage. The instructor's failed-release/rollback demonstration belongs to a later approved deployment stage.

References: [Helm charts/schema](https://helm.sh/docs/topics/charts/), [probe behavior](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/), [StatefulSet storage](https://kubernetes.io/docs/concepts/workloads/controllers/statefulset/).
