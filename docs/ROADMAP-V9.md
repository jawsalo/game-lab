# Game Lab — V9 Roadmap

**Status:** PHASE 2 IN PROGRESS — October 18, 2026  
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
Establish the versioned Grim Dawn item catalog, then add PostgreSQL-backed character/stash snapshot uploads, parsing and duplicate detection. Keep canonical game data separate from personal inventory, keep local exports read-only, and separate upload access from MCP privileges. **Exit:** useful persistent workload generating real traffic.

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

## Next work session — continue Phase 2
1. **Merge Catalog Foundation — 15 min:** review and merge the tested catalog branch after final CI checks.
2. **Design Inventory Snapshot Contract — 30–45 min:** define supported save/stash inputs, immutable upload metadata, ownership, and failure handling.
3. **Add PostgreSQL Foundation — 60–75 min:** deploy conservative persistent storage and credentials injection without coupling canonical item data to user inventory.

## Progress — October 18, 2026

- Deployed the mobile-first web shell and FastAPI service at `games.phobosandeimos.com`.
- Added same-origin `/api` routing, liveness/readiness probes, resource limits and non-root containers with read-only root filesystems.
- Added GitHub Actions image builds and immutable GHCR tags; K3s successfully pulled both images.
- Upgraded Helm chart from `0.1.0` to `0.2.0`; active release is revision 4.
- Exercised rollback behavior when NGINX lacked a writable temporary directory, then fixed it with a narrowly scoped ephemeral `/tmp` mount.
- Verified public HTTPS, browser-rendered status, API metadata and readiness.

**Phase 1 complete:** the application-foundation branch was merged into `main`; the parameterized deployment and public smoke-test workflow passed end to end at Helm revision 5.

### Phase 2 catalog checkpoint

- Recreated the GrimTools ingestion procedure from fresh browser-downloaded `1.3.1.0` sources and merged the reproducible pipeline into `jawsalo/grimtools-data`.
- Pinned the verified 11.6 MB SQLite artifact in the API build with source commit, size, and SHA-256 provenance.
- Added guarded catalog validation, read-only immutable SQLite access, metadata, item detail, full-text search, filters, pagination, and exact-name relevance ranking.
- Added a responsive web catalog with 8,695 searchable records and explicit separation from future personal inventory.
- Added eight catalog regression tests, catalog-aware readiness, CI validation, immutable image publication, retrying deployment smoke tests, and production catalog assertions.
- Deployed and verified the catalog at Helm revision 8 with API version `125cea4`.

**Phase 2 remains in progress:** canonical item search is complete; personal character/stash ingestion, PostgreSQL persistence, ownership, and duplicate detection remain.

## Resume checklist
- Merge the catalog branch, start from updated `main`, and verify Helm revision 8, both pods, and the catalog-aware public smoke test.
- Preserve the pinned canonical catalog as immutable reference data.
- Take a checkpoint / backup before PostgreSQL or personal inventory changes.
- Define the upload and ownership boundary before implementing save/stash parsing.
- Do not install monitoring infrastructure first or activate Datadog prematurely.

*Time estimates are rough hands-on sessions, not deadlines.*
