# Game Lab

Game Lab is an open-source, self-hosted platform for small, interchangeable game tools. It is designed for a lightweight K3s server without tying application code to one domain, host, or observability provider.

The deployment values file is the platform's equivalent of a parent pom.xml: environment-specific choices live there and flow into the chart.

## Design rules

- Application code never owns public hostnames.
- Kubernetes services communicate through service DNS names.
- Browser clients prefer same-origin paths such as /api.
- Modules are optional and declare their configuration inputs.
- Secrets stay outside Git and are injected at deploy time.
- A domain migration should primarily be one values-file change.

## Repository map

| Path | Purpose |
| --- | --- |
| apps/ | Deployable web, API, MCP, and worker applications |
| modules/ | Optional game-specific modules |
| deploy/chart/ | Reusable Helm chart |
| deploy/environments/ | Authoritative environment values |
| deploy/components/ | Independently managed platform components |
| scripts/ | Validation and configuration utilities |
| docs/ | Architecture and operations notes |

## Quick start

~~~bash
python3 -m pip install -r requirements.txt
make validate
make endpoints ENV=example
~~~

With Helm installed:

~~~bash
make helm-lint ENV=example
make helm-render ENV=example
~~~

The example environment is safe to copy. Personal secrets and machine-specific overrides belong in ignored *.local.yaml files or an external secret manager.

## Deployment

GitHub Actions publishes matching web and API images with immutable sha-<commit> tags. From a configured K3s host, deploy one tested image pair and run public smoke tests with:

~~~bash
scripts/deploy.sh sha-abcdef0 https://games.example.com
~~~

The command validates configuration, lints the chart, performs a rollback-on-failure Helm upgrade, waits for both rollouts, and verifies the public web and API routes. Override GAME_LAB_RELEASE, GAME_LAB_NAMESPACE, or GAME_LAB_VALUES when targeting another environment.

## Current status

Phase 2 is in progress, with the Grim Dawn catalog foundation running in production:

- The API packages a pinned, read-only Grim Dawn 1.3.1.0 SQLite catalog containing 8,695 records.
- Catalog provenance records the authoritative jawsalo/grimtools-data source commit, byte size, and SHA-256.
- /api/grim-dawn/catalog exposes version and facet metadata.
- /api/grim-dawn/items provides full-text search, filters, bounded pagination, and exact-match ranking.
- /api/grim-dawn/items/{id} returns one complete record by stable item ID.
- The mobile-first web interface searches the catalog through same-origin API routes.
- Validation checks the artifact, SQLite identity and integrity, embedded metadata, item/FTS counts, and regression queries.
- CI validates the repository before publishing matched immutable API and web images.
- Deployment smoke tests retry brief ingress handoffs and verify the live catalog.

The catalog describes the complete game item database. It is intentionally separate from personal inventory. The next Phase 2 slice will add read-only character/stash snapshot ingestion, persistence, and duplicate detection.

The OpenTelemetry API instrumentation and open-source observability stack are now deployed. Prometheus has confirmed API request metrics. Grafana is private; a beginner-friendly dashboard and user-facing logs/traces verification remain.

## Operations and handoff

- [V9 roadmap](docs/ROADMAP-V9.md) — project phases, decisions, and current checkpoint.
- [Session 3 handoff](docs/SESSION-3-HANDOFF.md) — latest stopping point and Grafana access steps.
- [Operator and succession runbook](docs/OPERATOR-RUNBOOK.md) — deployment, rollback, private Grafana access, recovery limits, and successor-access checklist.
- [Architecture notes](docs/architecture.md) and [operations baseline](docs/operations.md).

Secrets, recovery codes, private keys, kubeconfig files, and provider credentials must never be committed to the repository. The operator runbook lists what an owner needs to arrange privately and marks unverified recovery steps.

Licensed under Apache 2.0. Game names and third-party data remain the property of their respective owners.
