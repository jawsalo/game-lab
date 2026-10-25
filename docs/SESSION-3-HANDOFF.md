# Game Lab V9 — Session 3 Handoff

**Updated:** October 25, 2026  
**Repository:** `jawsalo/game-lab`  
**Roadmap:** [ROADMAP-V9.md](ROADMAP-V9.md)

## Stopping point

The phone-approved PR-to-VPS path is live and has completed its first production deployment. The **“Only show highest-level version”** catalog option is deployed, and the user verified that it works for Monster Infrequents and Legendaries.

This is a clean stopping point. Tomorrow, resume with the beginner-friendly Grafana dashboard and then verify the Loki logs and Tempo traces. The deployment workflow is operational; no setup or manual deploy needs to be repeated.

## Verified

- Prometheus, Grafana, Loki, Tempo, and Alloy are running in namespace `observability`.
- Grafana is private and is not exposed through the public ingress.
- Grafana was opened locally using a Kubernetes port-forward on the VPS and an SSH tunnel from the user's Windows PC.
- API requests were found in Prometheus under metric `http_server_duration_milliseconds_count`.
- Confirmed route series for `/api`, `/api/grim-dawn/catalog`, and `/api/grim-dawn/items`, each labeled `job="game-lab-api"`, `http_status_code="200"`, with three requests recorded at query time.
- The instrumented API deploy passed the public smoke test. A transient 502 line appeared during one deployment output, but the retrying smoke test completed successfully.
- Alloy's remote-write endpoint was corrected from port 9090 to the Prometheus Service port 80; Alloy was upgraded and restarted. Application metrics are subsequently visible in Prometheus.

## Phone-approved deployment — verified October 25, 2026

- GitHub ruleset **Protect Main** targets `main`, requires pull requests, and requires the four checks listed in [PULL-DEPLOY.md](PULL-DEPLOY.md).
- The VPS user timer is enabled and polls successful main builds every five minutes. Its first run recorded baseline `35ae6cd` without rolling production, as designed.
- Repository Actions variables are set: `GAME_LAB_AUTO_DEPLOY=true` and `GAME_LAB_BASE_URL=https://games.phobosandeimos.com`.
- PR #13 merged as `7d2e95f`. Its validation and image publishing passed; the VPS deployed it; **Verify production deployment** passed the live API version check and production smoke tests.
- The user checked the live catalog and confirmed **“Only show highest-level version”** works for Monster Infrequents and Legendaries.
- Use the ordinary PR review/merge path for future changes. Keep the timer enabled. Troubleshooting commands are in [PULL-DEPLOY.md](PULL-DEPLOY.md).


## Grafana access

Keep both forwarding processes running while using Grafana.

1. In an SSH shell on the VPS:
   ```bash
   kubectl -n observability port-forward svc/grafana 3000:80
   ```
2. In a separate Windows PowerShell window:
   ```powershell
   ssh -N -L 3000:127.0.0.1:3000 ubuntu@15.204.123.20
   ```
3. Open [http://localhost:3000](http://localhost:3000) in the PC browser.
4. Sign in as `admin` with the Grafana admin password the user saved during setup.

If the browser cannot connect, make sure both commands are still running. The Kubernetes port-forward is the VPS-to-Grafana leg; the SSH command carries that local VPS port to the PC.

## Next-session restart point

1. **Make Grafana understandable:** create a beginner-friendly Game Lab dashboard with request rate, response latency, and error rate. Use the Prometheus source already receiving API metrics.
2. **Verify the other signals:** use Grafana Explore to find Game Lab logs in Loki, then confirm API traces in Tempo. Record any missing configuration before changing it.
3. **Return to Phase 2:** define the character/stash snapshot upload and ownership contract before implementing PostgreSQL persistence or parsing.
4. Keep Datadog deferred until there is a meaningful workload and repeatable failure scenarios to compare.

## Current caveats

- A friendly Game Lab dashboard has not been created.
- Prometheus metrics are verified. Logs and traces are deployed as part of the stack but have not yet been confirmed through the user's Grafana workflow.
- No PostgreSQL-backed personal inventory or snapshot import is implemented yet.
- Do not expose Grafana publicly as part of dashboard setup.
