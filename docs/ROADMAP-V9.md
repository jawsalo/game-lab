# Game Lab — V9 Roadmap

**Status:** ADOPTED — October 13, 2026  
**Supersedes:** V8  
**Execution:** Not starting tonight. Resume with **“Resume Game Lab V9”**.

## Mission
Build a genuinely useful application on our existing K3s VPS, instrument it with vendor-neutral OpenTelemetry, run an open-source observability stack, introduce controlled MCP operations, then evaluate Datadog using real workloads and reproducible failures. Keep the system small, teachable, and portfolio-worthy.

## Existing foundation (previously verified; recheck before work)
- Ubuntu 24.04 VPS, single-node K3s v1.36.3+k3s1.
- Repository: `jawsalo/game-lab`; Helm deployment in `game-lab` namespace.
- Traefik ingress, DNS `games.phobosandeimos.com`, Let's Encrypt TLS, HTTPS endpoint previously verified.
- Previous capacity observation: ~22 GiB RAM, ~193 GiB disk. Verify current availability.
- Preserve working infrastructure; do not assume old health checks prove present state.

## Phases

### 1. Application foundation — 2–3 sessions
Inspect repo, cluster and Helm release. Replace placeholder with a mobile-friendly web frontend, backend API and health endpoints. Make GitHub-to-K3s deployment repeatable. **Exit:** reachable app and tested deployment workflow.

### 2. Persistent data and useful features — 3–5 sessions
Add PostgreSQL and actual features. Candidate first feature: Grim Dawn inventory snapshot upload, parsing and duplicate detection. Keep local export read-only and upload access separate from MCP privileges. **Exit:** useful persistent workload generating real traffic.

### 3. Vendor-neutral instrumentation — 1–2 sessions
Instrument API and background worker with OpenTelemetry: structured logs, HTTP metrics, DB timing, distributed traces and trace context. **Exit:** telemetry independent of a vendor backend.

### 4. Open-source observability — 3–4 sessions
Deploy Prometheus, Grafana, Loki, Tempo, and Alloy / OTel Collector in `observability` namespace. Start with conservative storage/resource limits and proposed seven-day metrics retention; validate capacity. **Exit:** correlated metrics, logs and traces.

### 5. Controlled MCP — 2–4 sessions
Begin with authenticated, audited read-only Grafana and Kubernetes access. Later add explicit-approval, allowlisted Kubernetes writes restricted to `game-lab`. Apply minimum RBAC and secrets/network controls. **Exit:** safe ChatGPT-assisted investigations and constrained operations.

### 6. Reliability engineering lab — 2–3 sessions
Add synthetic traffic, HTTP errors, slow queries, latency, resource saturation and failed deployments. Build alerts, SLOs, runbooks, backups and tested restore procedures. **Exit:** repeatable troubleshooting scenarios.

### 7. Datadog evaluation — trial duration TBD
**Do not start the trial yet.** Datadog's Jack Rotsart suggested personal Gmail might work for trial signup, but it is not guaranteed. Wait until app, telemetry and failure scenarios are ready. Compare Datadog to the open-source stack on service maps, correlation, alerts, investigation speed, MCP capabilities, cost and operational overhead. **Exit:** evidence-based vendor comparison.

### 8. AI-assisted operations and portfolio — ongoing
Unify application, Kubernetes, GitHub and observability context for guided investigations and carefully approved remediation. Document architecture, tradeoffs and demos relevant to observability architecture and technical leadership.

## Architecture and operating principles
- Keep it small: frontend + API + PostgreSQL + optional worker on one K3s node.
- Parameterize configuration; avoid hardcoded infrastructure values and unnecessary microservices.
- OpenTelemetry before choosing a monitoring backend.
- Separate read access, writes and secrets. Audit actions and require approval for consequential changes.
- Each chunk should be short, descriptive, understandable, testable and committed.
- The Grim Dawn parser is **not** a prerequisite for the first API deployment.

## Next two-hour work session (not tonight)
1. **Inspect Current Deployment — 20 min:** review GitHub, Helm values, pods and live HTTPS endpoint.
2. **Create Application Skeleton — 60 min:** frontend, API, health endpoints and parameterized configuration.
3. **Deploy and Verify — 40 min:** build, deploy, test on mobile and commit a working checkpoint.

## Resume checklist
- Verify current repo branch, Helm release, pods, DNS/TLS and VPS capacity.
- Take a checkpoint / backup before disruptive changes.
- Begin Chunk 1 and work sequentially.
- Do not install monitoring infrastructure first or activate Datadog prematurely.

*Time estimates are rough hands-on sessions, not deadlines.*
