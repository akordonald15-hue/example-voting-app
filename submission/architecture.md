# Architecture — configured flows and demonstrated scope

## Capstone 1: AWS Voting App

```mermaid
flowchart LR
  Git[Reviewed commit] --> CI[Hosted tests + Trivy]
  CI --> GHCR[Opt-in immutable GHCR publication]
  GHCR -. production automation NOT demonstrated .-> Server
  SSM[Private SSM access] --> Server
  subgraph AWS[Existing AWS K3s cluster]
    subgraph Server[Control plane: Voting App retained]
      Vote --> Redis --> Worker --> PG[PostgreSQL]
      PG --> Result
      PG --- PVC[Node-bound persistent claim]
    end
    NewWorker[Tainted worker: joined, no Robot Shop deployment]
  end
```

Deployment health/join are owner-confirmed checkpoints. Solid arrows show application topology, not fresh tests during packaging. Persistent local-path data must not be deleted; worker does not make the single control plane highly available.

## Capstone 2: demonstrated local kind topology

```mermaid
flowchart LR
  Load[1-user bounded load] --> Web
  subgraph Kind[Local kind: robot-shop namespace]
    Web --> Catalogue --> MongoDB
    Web --> Cart --> Redis
    Web --> User --> MongoDB
    Web --> Shipping --> MySQL
    Web --> Payment --> MQ[RabbitMQ]
    Payment --> Gateway[Simulated gateway]
    Ratings --> MySQL
    MQ --> Dispatch
  end
  subgraph Obs[Local observability namespace]
    Prom[Prometheus RED + availability] --> Grafana
    Fluent[Fluent Bit] --> Loki
    OTEL[OTel Collector] --> Jaeger
    Prom --> Alerts[Alert evaluation]
  end
  Kind -. metrics .-> Prom
  Kind -. logs .-> Fluent
  Catalogue -. retrieved HTTP spans .-> OTEL
  Alerts -. Slack delivery NOT demonstrated .-> Slack
```

Application checkout, metrics, selected logs/traces and local incident have separate receipts. Diagram arrows are not proof of complete distributed checkout tracing. AWS overlays describe a planned topology only. Existing upstream application image: [Voting App architecture](../architecture.excalidraw.png).
