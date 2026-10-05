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
python3 -m pip install -r requirements-dev.txt
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

This first milestone establishes the deployment contract and a small HTTPS-ready placeholder workload. Installation of cert-manager, DNS changes, firewall changes, and production deployment are deliberately separate operations.

Licensed under Apache 2.0. Game names and third-party data remain the property of their respective owners.
