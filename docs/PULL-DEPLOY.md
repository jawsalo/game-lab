# Phone-approved pull deployment

## What it does

After a reviewed pull request is merged to `main`, GitHub Actions validates the
commit and publishes its immutable `sha-<commit>` API and web images. A timer on
the VPS checks GitHub's public Actions results every five minutes. It deploys
only when the latest main-branch image build and the full validation workflow
both succeeded for the same commit. It then runs the existing Helm rollout,
readiness checks, and public smoke tests from that exact commit.

The VPS needs no GitHub token or deploy SSH key. GitHub Actions does not need
VPS SSH access, and no self-hosted GitHub runner is installed on the VPS. The
VPS pull service uses the existing operator account and its current Kubernetes
access. Logs go to the user's systemd journal.

## First-time VPS setup

Run once on the VPS after this change has been merged. This creates a separate
checkout so the deployer never changes the operator's interactive `~/game-lab`
working tree, installs Python dependencies in a dedicated virtual environment,
and enables a user-level systemd timer:

```bash
cd ~/game-lab
git pull --ff-only
bash scripts/install-pull-deployer.sh https://games.example.com
```

Replace the example host with the production HTTPS origin, without a path.

The installer checks that the current Kubernetes and Helm access can read the
existing application before enabling the timer. It enables user lingering so
the timer continues after logout and starts again after a reboot.

**The first successful timer run only records the current validated main build
as its baseline. It does not roll production.** This avoids an unexpected
catch-up rollout when the pull service is first installed. Later successful
builds on `main` trigger deployment. The state file is stored under
`~/.local/state/game-lab-pull-deploy/state.json`.

## GitHub configuration

The deployment check itself enforces that both of these workflows completed
successfully on the candidate commit:

- `Validate` — secret scan, Helm lint/render, portability checks, and tests.
- `Build application images` — repository validation and both immutable GHCR
  images published successfully.

Configure the `main` branch to require pull requests and the `Validate`
workflow's successful check before merging. Keep the image-build checks
required for application and deployment changes. The image build workflow runs
on every pull request so its PR checks are available consistently; those PR
builds have no package-publish permission. Only trusted push builds receive
`packages: write`.

After the VPS timer is installed and its first baseline is recorded, add these
repository Actions variables to turn on the post-deployment verification job:

| Variable | Value |
| --- | --- |
| `GAME_LAB_AUTO_DEPLOY` | `true` |
| `GAME_LAB_BASE_URL` | Production HTTPS origin, such as `https://games.example.com` |

For each successful main push, that job waits up to 15 minutes for the public
API to report the expected commit version, then runs the existing full smoke
test. This makes deployment success or failure visible in the GitHub Actions
run that built the images. Leave the variable unset until the VPS timer has
been installed and checked.

## Day-to-day use and troubleshooting

Review and merge a PR from GitHub on the phone after its checks pass. Open the
`Build application images` run for the merge commit. Once enabled, it will show
`Verify production deployment`; a green check means the rollout and smoke tests
passed. A red check includes the timeout or smoke-test failure.

On the VPS, timer state and service output are available with:

```bash
systemctl --user list-timers game-lab-pull-deploy.timer
journalctl --user -u game-lab-pull-deploy.service -n 100 --no-pager
```

The puller fails closed: it does nothing while either workflow is pending or
failed, refuses commits outside current `main`, refuses rewritten history, and
does not advance its saved SHA unless Helm rollout, readiness, smoke tests, and
the live API version all match. Helm uses its existing rollback-on-failure
behavior. If application smoke tests fail after a successful Helm upgrade,
inspect `helm -n game-lab history game-lab` and use the manual rollback
procedure in [the operator runbook](OPERATOR-RUNBOOK.md).

Disable polling without deleting configuration:

```bash
systemctl --user disable --now game-lab-pull-deploy.timer
```

## Boundaries and remaining manual checks

- Main-branch merges remain the human approval point. The current GitHub
  connection could not inspect branch-protection settings, so verify those
  settings in the repository before relying on them.
- The service has the operator account's existing namespace deployment access;
  it does not add a new Kubernetes account or broaden cluster permissions.
- The service reports through systemd logs and, when enabled, the GitHub Actions
  deployment-verification job. It does not perform unattended remediation.
- This changes repository automation only. It does not install or enable the
  timer on the VPS; setup is a separate, explicit operator step.
