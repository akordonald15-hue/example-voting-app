# Example Voting App

## AWS DevOps Capstone 1 — Ship It

**Submission entry point (October 26, 2026):** [current evidence, rubric status and submission instructions](docs/submission-readiness.md).
Earlier audits are historical checkpoints; use this entry point for current claims.
Robot Shop is maintained separately under [capstone2](capstone2/README.md).
The existing AWS t3.medium cannot fit the proposed combined resource requests.
Never delete the Voting App PostgreSQL volume for a demo.

The capstone deployment uses **one Helm chart**, Terraform-managed AWS EC2/K3s,
GHCR digest-pinned images, private SSM browser access and persistent PostgreSQL.
The owner reports healthy Helm revision **2 deployed**, five Ready workloads and
successful browser voting/live-score updates. Preserve that database; historical
recovery procedures must not be rerun.

Start with the [submission guide, architecture, CI/CD limitations and evidence](docs/submission-readiness.md).
The chart is [helm/voting-app](helm/voting-app/README.md), infrastructure code is
[terraform](terraform/), and the proposed pipeline is
[capstone.yaml](.github/workflows/capstone.yaml). Hosted testing, all-severity
scanning and GHCR publication succeeded for the recorded release. Production
deployment is a separate, unproven automation gate; Terraform destroy/recreate
has **not been demonstrated**. The [isolated local Helm rollback](docs/rollback-evidence/README.md)
passed using a Vote-only fixture, not the full production application.
Publication and deployment are independently opt-in. The upstream examples below are background, **not
the capstone deployment procedure**; do not apply the legacy NodePort manifests
to the working cluster.

Local validation uses `scripts/validate-helm.py` (Helm + PyYAML) and
`scripts/test-stage5-local.py` (disposable Docker integration with explicit image
IDs). The pipeline builds each Dockerfile's `final` target before testing it.
No public ingress, Docker Hub credentials or public Kubernetes API are required.

A simple distributed application running across multiple Docker containers.

## Getting started

Download [Docker Desktop](https://www.docker.com/products/docker-desktop) for Mac or Windows. [Docker Compose](https://docs.docker.com/compose) will be automatically installed. On Linux, make sure you have the latest version of [Compose](https://docs.docker.com/compose/install/).

This solution uses Python, Node.js, .NET, with Redis for messaging and Postgres for storage.

Run in this directory to build and run the app:

```shell
docker compose up
```

The `vote` app will be running at [http://localhost:8080](http://localhost:8080), and the `results` will be at [http://localhost:8081](http://localhost:8081).

Alternately, if you want to run it on a [Docker Swarm](https://docs.docker.com/engine/swarm/), first make sure you have a swarm. If you don't, run:

```shell
docker swarm init
```

Once you have your swarm, in this directory run:

```shell
docker stack deploy --compose-file docker-stack.yml vote
```

## Run the app in Kubernetes

The folder k8s-specifications contains the YAML specifications of the Voting App's services.

Run the following command to create the deployments and services. Note it will create these resources in your current namespace (`default` if you haven't changed it.)

```shell
kubectl create -f k8s-specifications/
```

The `vote` web app is then available on port 31000 on each host of the cluster, the `result` web app is available on port 31001.

To remove them, run:

```shell
kubectl delete -f k8s-specifications/
```

## Architecture

![Architecture diagram](architecture.excalidraw.png)

* A front-end web app in [Python](/vote) which lets you vote between two options
* A [Redis](https://hub.docker.com/_/redis/) which collects new votes
* A [.NET](/worker/) worker which consumes votes and stores them in…
* A [Postgres](https://hub.docker.com/_/postgres/) database backed by a Docker volume
* A [Node.js](/result) web app which shows the results of the voting in real time

## Notes

The voting application only accepts one vote per client browser. It does not register additional votes if a vote has already been submitted from a client.

This isn't an example of a properly architected perfectly designed distributed app... it's just a simple
example of the various types of pieces and languages you might see (queues, persistent data, etc), and how to
deal with them in Docker at a basic level.
