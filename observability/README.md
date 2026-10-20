# Open-source observability

This is a standalone platform release in the `observability` namespace. It does not depend on or modify the Game Lab application Helm release.

## Components and retention

| Component | Deployment | Persistent storage | Retention |
| --- | --- | ---: | --- |
| Prometheus | Standalone server | 8 GiB | 7 days, 6 GiB cap |
| Grafana | Single replica, ClusterIP only | 1 GiB | Dashboards and local state |
| Loki | Monolithic, filesystem | 8 GiB | 7 days |
| Tempo | Single binary, local storage | 5 GiB | 3 days |
| Alloy | One Deployment | None | Forwards OTLP, reads Kubernetes pod logs |

The stack requests about 0.8 CPU and 1.5 GiB memory. Container limits total about 3.5 CPU and 3.5 GiB memory. These are ceilings, not expected steady-state use. It asks for 22 GiB of persistent volume capacity, and the deployment script requires at least 30 GiB free on the host so the node has room for growth and other workloads.

Grafana has no Ingress or LoadBalancer. Reach it through a local tunnel:

```sh
kubectl -n observability port-forward svc/grafana 3000:80
```

Then open `http://127.0.0.1:3000`. The admin password is entered without echo by the deployment script and stored in a Kubernetes Secret; it is not committed.

## Deploy

From the repository root on the VPS, after pulling the branch/merge that contains these files:

```sh
bash scripts/deploy-observability.sh
```

The script shows the Kubernetes context, node utilization, and host disk usage before any cluster changes. It stops if `kubectl top nodes` is unavailable or host disk free space is below 30 GiB. Confirm at least 4 GiB of node memory remains available, then type `deploy` at the prompt. No public route is created.

The chart versions are pinned in the deployment script. Their upstream sources are:

- Prometheus: `prometheus-community/prometheus`
- Grafana, Loki, and Tempo: `grafana-community/helm-charts`
- Alloy: `grafana/alloy`

Alloy accepts OTLP/gRPC on port 4317 and OTLP/HTTP on port 4318 inside the cluster. It forwards metrics to Prometheus remote-write, traces to Tempo, OTLP logs to Loki, and Kubernetes pod logs to Loki. The Grafana datasources are provisioned from `values/grafana.yaml`.

The application export endpoint is deliberately not set by this stack deployment. After the stack is healthy, configure the API's OTLP endpoint as `alloy.observability.svc.cluster.local:4317` in the Game Lab Helm values and deploy the instrumented API image. That later app deployment is the point at which application telemetry begins flowing.

## Verify

```sh
kubectl -n observability get pods,pvc
helm -n observability list
kubectl -n observability port-forward svc/grafana 3000:80
```

In Grafana, verify the Prometheus, Loki, and Tempo data sources show as healthy. Then deploy the API OTLP endpoint and check for API request metrics and traces. A temporary API log line should appear in Loki from Alloy's Kubernetes pod-log source.

## Operational notes

- Keep this stack internal. Do not add public Grafana ingress.
- The single-node deployment has no high availability. Keep backups of anything important outside this namespace.
- Retention and storage limits are intentionally short and small for a learning lab. Loki's filesystem backend and local Tempo storage are suitable for this single-node lab profile; evaluate object storage before scaling or treating telemetry as durable records.
