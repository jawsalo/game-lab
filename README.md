# Game Lab

Game Lab is an open-source, self-hosted platform for small, interchangeable game tools. It is designed for a lightweight K3s server without tying application code to one domain, host, or observability provider.

The deployment values file is the platform's equivalent of a parent `pom.xml`: environment-specific choices live there and flow into the chart.

## Design rules

- Application code never owns public hostnames.
- Kubernetes services communicate through service DNS names.
- Browser clients prefer same-origin paths such as `/api`.
- Modules are optional and declare their configuration inputs.
- Secrets stay outside Git and are injected at deploy time.
- A domain migration should primarily be one values-file change.

## Repository map

| Path | Purpose |
| --- | --- |
| `apps/` | Deployable web, API, MCP, and worker applications |
| `modules/` | Optional game-specific modules |
| `deploy/chart/` | Reusable Helm chart |
| `deploy/environments/` | Authoritative environment values |
| `deploy/components/` | Independently managed platform components |
| `scripts/` | Validation and configuration utilities |
| `docs/` | Architecture and operations notes |

## Quick start

```bash
python3 -m pip install -r requirements.txt
make validate
make endpoints ENV=example
```

With Helm installed:

```bash
make helm-lint ENV=example
make helm-render ENV=example
```

The example environment is safe to copy. Personal secrets and machine-specific overrides belong in ignored `*.local.yaml` files or an external secret manager.

## Current status

Phase 1 application foundation is running:

- A mobile-first static web shell is served by an unprivileged NGINX container.
- A FastAPI service exposes metadata plus liveness and readiness endpoints.
- Traefik routes same-origin `/api` requests to the API service.
- GitHub Actions builds and publishes immutable web and API images to GHCR.
- Helm chart `0.2.0` deploys both workloads with non-root security contexts, read-only root filesystems, health probes, and resource limits.

The remaining Phase 1 work is to automate the currently manual GitHub-to-K3s deployment path and add deployment smoke tests.

Licensed under Apache 2.0. Game names and third-party data remain the property of their respective owners.
