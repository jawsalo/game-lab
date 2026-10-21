# Game Lab Operator and Succession Runbook

**Last reviewed:** October 21, 2026  
**Purpose:** Give a trusted successor enough context to preserve the service, diagnose common failures, and avoid losing data or access.  
**Status:** Application and observability stack are running. Backup and account-recovery procedures are not yet verified. Keep this document current as infrastructure changes.

## Service and infrastructure at a glance

| Area | Current record |
| --- | --- |
| GitHub repository | [jawsalo/game-lab](https://github.com/jawsalo/game-lab), default branch main |
| Public web address | [https://games.phobosandeimos.com](https://games.phobosandeimos.com) |
| VPS | Host vps-a8605df4, Ubuntu 24.04, public IP 15.204.123.20 |
| Kubernetes | Single-node K3s; version last reported as v1.36.3+k3s1 |
| Application namespace | game-lab |
| Observability namespace | observability |
| Ingress | Traefik on ports 80 and 443; TLS issued by cert-manager / Let's Encrypt |
| Application | Web frontend and FastAPI API; Grim Dawn 1.3.1.0 catalog (8,695 records) |
| Telemetry | API exports to Alloy; Prometheus has confirmed API request metrics. Grafana is private. |
| Persistent personal data | PostgreSQL and character/stash imports are not implemented yet. |
| Backup and restore | Provider snapshot status and a tested recovery procedure are **not verified**. |

Host capacity figures in older notes are only a point-in-time estimate. Recheck current RAM, disk, Kubernetes node health, and persistent volume claims before installing or restoring services.

## What runs where

- The public request enters Traefik, which routes the web and same-origin API paths to the game-lab namespace.
- The web and API images are built by GitHub Actions and published to GHCR with immutable sha-<commit> tags.
- Kubernetes runs the application. Helm release game-lab describes its deployment.
- The API reads a pinned SQLite catalog packaged with the image. It is read-only canonical game data, not the user's personal stash.
- OpenTelemetry sends API telemetry to Alloy in observability. Alloy forwards metrics to Prometheus and is configured to collect cluster logs and send telemetry to Loki and Tempo.
- Grafana queries the observability backends. Grafana is intentionally not exposed through the public ingress.
- Observability and app data are stored on cluster PVCs using the VPS's local-path storage. A PVC is storage, not a backup.

## First response: check before changing anything

SSH to the VPS:

~~~bash
ssh ubuntu@15.204.123.20
cd ~/game-lab
~~~

Check the repository, node, releases, pods, and storage:

~~~bash
git status --short --branch
git log -1 --oneline
kubectl get nodes -o wide
kubectl get pods -A
helm -n game-lab status game-lab
helm -n observability list
kubectl -n observability get pvc
df -h /
~~~

If kubectl or Helm is unavailable, stop and confirm the K3s service and kubeconfig before changing firewall rules or reinstalling the cluster. Preserve SSH access. Do not delete PVCs, uninstall K3s, or reinstall the VPS as an exploratory troubleshooting step.

## Application release procedure

The repository is the source of truth for application and deployment configuration. Review the changes and GitHub Actions validation/image-build results before deploying.

On the VPS:

~~~bash
cd ~/game-lab
git pull --ff-only
source .venv/bin/activate
make validate
~~~

If the virtual environment does not exist, create it and install the repository requirements before validating:

~~~bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt -r apps/api/requirements.txt
make validate
~~~

Deploy the immutable image tag produced for the tested commit:

~~~bash
scripts/deploy.sh sha-<7-to-40-character-commit-sha> https://games.phobosandeimos.com
~~~

The script validates the repo, lints the Helm chart, upgrades the game-lab release with rollback-on-failure and a rollout wait, then runs public smoke tests. The tag must be the commit's exact sha- image tag, not latest. Do not continue if validation fails or the corresponding images were not published.

After deployment, confirm the script's smoke test passed. If a deployment fails, inspect the Helm status, pod events, and logs before retrying:

~~~bash
helm -n game-lab status game-lab
helm -n game-lab history game-lab
kubectl -n game-lab get pods -o wide
kubectl -n game-lab get events --sort-by=.metadata.creationTimestamp
kubectl -n game-lab logs deployment/game-lab-api --previous
kubectl -n game-lab logs deployment/game-lab-api
~~~

### Roll back an unhealthy application release

First inspect history and choose the last known-good revision:

~~~bash
helm -n game-lab history game-lab
helm -n game-lab rollback game-lab <known-good-revision> --wait --timeout 5m
kubectl -n game-lab rollout status deployment/game-lab-api
kubectl -n game-lab rollout status deployment/game-lab-web
scripts/smoke-test.sh https://games.phobosandeimos.com <expected-api-version>
~~~

A Helm rollback changes the application release. It does not restore lost persistent data or undo unrelated cluster changes. Do not use helm uninstall as a normal rollback.

## Observability operations

The pinned deployment procedure is in scripts/deploy-observability.sh; configuration is under observability/. The deployment script checks node and disk capacity, renders pinned charts, asks for confirmation, and prompts for the Grafana admin password. Never put that password in a shell-history command, source control, or this document.

Check component health:

~~~bash
kubectl -n observability get deployments,statefulsets,pods,pvc
helm -n observability list
kubectl -n observability get services
~~~

If an Alloy ConfigMap has changed, restart Alloy so the running process loads the new configuration:

~~~bash
kubectl -n observability rollout restart deployment/alloy
kubectl -n observability rollout status deployment/alloy
~~~

API metric ingestion was verified by querying Prometheus for http_server_duration_milliseconds_count with job="game-lab-api". Logs and traces have not yet had a complete user-facing verification in Grafana.

### Open Grafana privately

Use two forwarding processes; keep both running while Grafana is open.

1. In an SSH shell on the VPS:
   ~~~bash
   kubectl -n observability port-forward svc/grafana 3000:80
   ~~~
2. In a separate PowerShell window on the PC:
   ~~~powershell
   ssh -N -L 3000:127.0.0.1:3000 ubuntu@15.204.123.20
   ~~~
3. Browse to [http://localhost:3000](http://localhost:3000). The username is admin; the admin password was selected at observability installation and is held outside this repository.

Do not add a public Grafana ingress to make access easier. If the local page refuses the connection, confirm both forwarding commands remain active before debugging Grafana itself.

## Recovery and data preservation

### What can be rebuilt from GitHub

- Application manifests and Helm chart are in this repository.
- The pinned catalog and API code are versioned/reproducible through the repository's documented GrimTools source provenance and image build.
- Observability chart values and Alloy configuration are in observability/.
- GitHub Actions can rebuild application images from a validated commit.

### What is not yet proven recoverable

- Provider-level VPS backup/snapshot availability, retention, and restore steps are unknown.
- The observability PVCs use node-local storage. If the VPS disk is lost, stored metrics, logs, traces, and Grafana state may be lost unless a separate backup exists.
- There is no PostgreSQL personal-inventory database yet, but future data must not be considered safe until backups are copied off the VPS and a restore has been tested.
- A clean-room rebuild of the VPS, DNS, TLS issuer, and K3s cluster has not been rehearsed.

Until backup and restore are verified, treat the VPS as a single point of failure. Before changing storage, reinstalling K3s, or rebuilding the host, preserve a provider snapshot if one is available and make a separate copy of any data that matters. Do not assume a bound PVC or a provider's advertised backup feature is a tested restore.

### Recovery order after VPS loss

1. Secure or recover the VPS provider account and inspect available snapshots before provisioning or deleting anything.
2. Recover GitHub owner access and check out the latest validated main branch.
3. Recover DNS/registrar access and confirm the domain still points where intended.
4. Provision a replacement host; install K3s and required cluster components from the current repository/runbooks.
5. Restore backed-up application data and secrets through secure channels. Never restore by committing secrets.
6. Deploy the application and observability stack using the repository procedures.
7. Verify DNS, TLS, health/readiness, catalog search, telemetry, and any restored data before considering recovery complete.

Steps 1, 3, 4, and 5 are not yet documented or tested end to end. Use this list as a work plan, not a validated recovery recipe.

## Successor access checklist — owner to complete privately

Keep account recovery details in a password manager with emergency access or another secure mechanism. Do not place passwords, API tokens, private SSH keys, kubeconfig files, recovery codes, Grafana secrets, or provider credentials in GitHub.

- [ ] Name a trusted successor and tell them where the secure credential handoff is stored.
- [ ] Ensure they can recover GitHub owner/repository access using an appropriate collaborator, organization, or account-recovery arrangement. Do not share the owner's personal login as the routine method.
- [ ] Ensure they can recover the OVHcloud VPS account and complete its second-factor challenge.
- [ ] Ensure they can recover DNS registrar access. The registrar and current access arrangement need to be recorded privately.
- [ ] Store the SSH key or alternate VPS console/recovery path in the secure handoff; verify access from a separate device/account.
- [ ] Store the Grafana admin password and explain how to rotate it through the Kubernetes secret/deployment procedure.
- [ ] Secure a copy of any K3s admin kubeconfig only in the designated encrypted credential storage. It grants cluster-wide authority.
- [ ] Verify any provider backup plan and complete a restore to a separate target before relying on it.
- [ ] When PostgreSQL or user data is added, implement off-host backups, retention, encryption, and scheduled restore tests before storing valuable data.

**Current state:** successor identity, provider/registrar recovery, secret storage location, and successful alternate-access test have not been provided or verified.

## Repository navigation

- README.md: project summary, quick start, and deployment entry point.
- docs/ROADMAP-V9.md: phased product and platform plan.
- docs/SESSION-3-HANDOFF.md: latest session stopping point and next observability tasks.
- docs/architecture.md: configuration and service-boundary decisions.
- docs/operations.md: initial deployment baseline.
- scripts/deploy.sh: validated application deployment and smoke test.
- scripts/deploy-observability.sh: capacity-gated observability installation.
- observability/: pinned values, Alloy pipeline, and dashboards/configuration.

## Change log

- 2026-10-21: Initial succession-oriented operator guide. Verified procedures and unresolved access/backup gaps are explicitly separated.
