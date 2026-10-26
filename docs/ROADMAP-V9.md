# Game Lab — V9 Roadmap

**Status:** PHASE 2 IN PROGRESS; PHASE 3 COMPLETE; PHASE 4 COMPLETE — metrics, logs, traces, and database-span correlation verified; PHONE-APPROVED DEPLOYMENT VERIFIED; MOBILE ITEM-CARD FIXES VERIFIED ON PRODUCTION — October 26, 2026  
**Supersedes:** V8  
**Execution:** Continue with short, validated chunks from the current Phase 2 checkpoint.

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

## Exploratory design note — phone-first, model-neutral operations

- **Learning is the short-term goal; the Game Lab app is the hobby workload** used to practice observability. Prefer repeatable exercises that build transferable skills across Dynatrace, Datadog, New Relic, and LGTM.
- Treat phone access as a first-class requirement so useful investigation fits into short gaps during work and family life.
- Build telemetry and a readable incident report first. A future report could collect the alert, relevant logs/metrics/traces, health checks, and recent deployment context on the VPS.
- Explore a model-neutral handoff: ChatGPT (or another assistant) can read the evidence and recommend a fixed runbook; Claude (or another MCP-capable client) may be given only specific, allowlisted write actions. Keep human approval, server-side target checks, audit records, and post-action verification in the runbook service.
- Initially, an alert should create evidence for a person and assistant to review; it should not directly launch an unattended remediation. Consider more automation only after the alert patterns and runbooks are proven.
- Verify that the intended assistant can use its MCP connection from a phone before selecting a paid tier or relying on that client. ChatGPT custom MCP availability and permissions vary by plan and client.

## Phone-approved PR deployment to VPS — completed October 25, 2026

**Goal achieved:** A reviewed PR can be merged from a phone, pulled by the VPS, deployed to K3s, and verified in GitHub without an interactive SSH deployment session.

- Active GitHub ruleset targets `refs/heads/main`, requires pull requests, and requires the four CI checks documented in [PULL-DEPLOY.md](PULL-DEPLOY.md).
- The VPS runs the user-level `game-lab-pull-deploy.timer` every five minutes from a separate deployer checkout. It uses no GitHub token or deploy SSH key.
- The first timer run recorded baseline `35ae6cd` and correctly made no rollout. The user then configured the Actions variables `GAME_LAB_AUTO_DEPLOY=true` and `GAME_LAB_BASE_URL` set to the production HTTPS origin, and enabled the timer.
- PR #13 added the opt-in **“Only show highest-level version”** catalog checkbox and API filtering. It groups Standard, Empowered, Elite, and Mythical name tiers by item group, category, and slot, applies highest-level selection before pagination, and preserves existing behavior by default.
- PR #13 merged as `7d2e95f`. The VPS timer deployed it; GitHub's **Verify production deployment** job passed its live-version check and smoke tests. The user confirmed on the website that filtering works for Monster Infrequents and Legendaries.

**Operational path:** Review and merge a PR; monitor the merge commit's **Build application images** and **Verify production deployment** workflows. Use the timer/journal commands in [PULL-DEPLOY.md](PULL-DEPLOY.md) if deployment status needs diagnosis. Do not manually deploy the same commit unless the automated path reports a failure.

## Architecture and operating principles
- Keep it small: frontend + API + PostgreSQL + optional worker on one K3s node.
- Parameterize configuration; avoid hardcoded infrastructure values and unnecessary microservices.
- OpenTelemetry before choosing a monitoring backend.
- Separate read access, writes and secrets. Audit actions and require approval for consequential changes.
- Each chunk should be short, descriptive, understandable, testable and committed.
- The Grim Dawn parser is **not** a prerequisite for the first API deployment.

## Current work — Phase 2 feature work with Phase 3/4 observability now active
1. **Grim Dawn catalog and item cards are deployed:** catalog search, filters, item details, structured item-card API and web rendering are live. PR #3 merged; the production catalog is pinned to Grim Dawn 1.3.1.0 with 8,695 records.
2. **OpenTelemetry API instrumentation is deployed:** FastAPI request metrics/traces and SQLite statement spans are enabled, with lifecycle management compatible with the current FastAPI version.
3. **Open-source stack is deployed:** Prometheus, Grafana, Loki, Tempo, and Alloy are running in the separate `observability` namespace. Grafana remains private.
4. **API metrics are confirmed end to end:** requests to `/api`, `/api/grim-dawn/catalog`, and `/api/grim-dawn/items` appeared in Prometheus as `http_server_duration_milliseconds_count`, labeled with `job="game-lab-api"` and HTTP 200.
5. **Alloy remote-write endpoint was corrected** to use the Prometheus Service port 80, and Alloy was upgraded/restarted. The Prometheus metric query confirms application metrics are arriving.
6. **Grafana dashboard and all telemetry signals are verified end to end** (October 26, 2026). The provisioned Game Lab dashboard shows API request rate, p95 latency, and 5xx rate. Loki returns API pod logs. A Tempo trace for `GET /api/grim-dawn/items` contains its SQLite `PRAGMA` and `SELECT` child spans, confirming trace correlation.
7. **Phase 2 remains in progress:** personal character/stash snapshot contract, PostgreSQL persistence, ownership, parsing and duplicate detection remain. Small item-card fidelity fixes are the active work before returning to the larger snapshot feature.

### Mobile item-card checkpoint — October 26, 2026

- PR #17 fixed Mythical-tier naming so the highest-level filter can return the correctly named Mythical item; the user verified the filter still behaves correctly.
- PR #18 removed the duplicate flavor description from expanded item details; the user confirmed the card no longer repeats it.
- PRs #19–20 added player-facing names for character stats and resistance types, including Cunning, Physique, Spirit, Health, and the damage-type resistances. The user verified the Cunning and resistance changes on mobile.
- PR #21 merged as `391688b`, adding GrimTools-style min/max rolls for variable equipment stats and Acid Retaliation, and rendering the Black Matriarch poison stat as `70/95 Poison Damage over 5 Seconds`.
- **Production verified:** `/api` reports version `391688b`; the live `it9040` card payload contains the expected ranges and 5-second poison duration, and the live web asset contains the updated Cunning, Acid Retaliation, and duration-aware label logic.
- The four canonical cards remain the acceptance set in [ITEM-CARD-BASELINE.md](ITEM-CARD-BASELINE.md). This skill-card chunk adds a generated, version-pinned lookup from the GrimTools 1.3.1.0 item database and English localization. It resolves skill data for 6,002 catalog items with source hashes recorded in the catalog provenance.
- The Black Matriarch API card now resolves its four +2 bonuses (Cadence, Curse of Frailty, Nidalla’s Hidden Hand, Righteous Fervor) and its level-two Venom of the Black Matriarch proc: trigger, description, recharge, duration, poison damage, and physical resistance reduction. The mobile details view renders these as separate Skill Bonuses and Granted Skills sections.
- **Next verification:** after both data and app PRs merge and deploy, verify the Black Matriarch card, then review Serenity, Blueprint: Relic - Serenity, and Dauntless against the four-card baseline. Keep broader skill and property-label ordering as follow-up polish; then return to the snapshot upload/ownership feature.

### Open-source observability verification — October 26, 2026
- Merged PR #15 and explicitly upgraded the observability Helm releases from the VPS. Grafana remains private.
- Prometheus metrics are visible in the provisioned Grafana dashboard; the screenshot showed `/api` traffic, about 4.7 ms p95 latency, and 0% 5xx at that time.
- Loki returned API pod logs, including successful 200 requests to the API, catalog, and item search routes.
- Tempo returned a `GET /api/grim-dawn/items` trace with six spans: the request, two HTTP send spans, one SQLite `PRAGMA`, and two SQLite `SELECT` spans. The database spans are children of the request trace.
- Dashboard, logs, traces, and database-span correlation are now verified. Continue Phase 2 with the snapshot upload and ownership contract before implementing persistence.

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

### Item cards checkpoint — October 20, 2026
- Added the structured card API and rendered descriptions, properties, conversions, recipes, and expansion IDs in the web interface.
- The four cards documented in [the item-card baseline](ITEM-CARD-BASELINE.md) are the canonical regression set for item-card translation, API, and UI changes.
- Product requirement: give users an **“Only show highest-level version”** option in catalog results. Delivered and verified on October 25, 2026; see the deployment checkpoint below.
- Merged PR #3 and deployed API/web image `sha-9fc6cbd`; Helm revision 9 rolled out both pods and the public smoke test passed.
- Production remains on the pinned 1.3.1.0 Grim Dawn catalog with 8,695 records.

### OpenTelemetry API foundation — now deployed and exporting
- Merged the API instrumentation with optional OTLP/gRPC trace and metric exporters, FastAPI request instrumentation, and SQLite statement spans.
- Configured the API to export to Alloy at `http://alloy.observability.svc.cluster.local:4317`.
- Fixed Alloy's Prometheus remote-write destination to use `prometheus-server.observability.svc.cluster.local:80`, then upgraded Alloy.
- Queried Prometheus and confirmed three successful requests each for `/api`, `/api/grim-dawn/catalog`, and `/api/grim-dawn/items`.

### Session 3 stopping point — October 21, 2026
The OSS observability stack and the API-to-Alloy-to-Prometheus metrics path are verified. The user has accessed Grafana and the provisioned dashboard, logs, traces, and SQLite span correlation are working. See [Session 3 handoff](SESSION-3-HANDOFF.md) for access steps and current next actions.

## Succession-readiness checkpoint — October 21, 2026

- Added [the operator and succession runbook](OPERATOR-RUNBOOK.md), covering the known topology, application deploy/rollback, private Grafana access, recovery limits, and a private successor-access checklist.
- Added its entry point to the repository README.
- Provider snapshots, off-host backups, disaster recovery, DNS/registrar recovery, and alternate successor access remain unverified. Do not describe the project as recoverable until restoration has been tested.

## Resume checklist
- Keep Grafana private; access it with the two-step port-forward and SSH tunnel documented in the session handoff.
- The phone-approved PR-to-K3s deployment workflow is complete and verified. Preserve it as the default path for future production changes.
- Open-source observability is complete for this checkpoint: dashboard, Loki logs, Tempo traces, and SQLite span correlation are verified.
- Merge and deploy the source-backed skill lookup plus Black Matriarch card changes, verify the production card, then retest the other three canonical cards. After that, return to Phase 2: define the personal snapshot upload/ownership contract, check current VPS capacity, and plan PostgreSQL persistence before changing production.
- Do not activate Datadog prematurely; wait for a meaningful workload and repeatable failure scenarios.

*Time estimates are rough hands-on sessions, not deadlines.*
