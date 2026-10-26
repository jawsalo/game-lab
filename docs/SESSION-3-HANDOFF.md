# Game Lab V9 — Session 3 Handoff

**Updated:** October 26, 2026  
**Repository:** `jawsalo/game-lab`  
**Roadmap:** [ROADMAP-V9.md](ROADMAP-V9.md)

## Stopping point

The phone-approved PR-to-VPS path is live and has completed production deployments. The **“Only show highest-level version”** catalog option was verified for Monster Infrequents and Legendaries. Grafana metrics, Loki logs, Tempo traces, and SQLite span correlation are also verified end to end.

The latest application change is PR #21, merged as `391688b`. It adds GrimTools-style stat ranges and fixes several Black Matriarch labels, including its combined poison damage-over-time line. Check the GitHub **Verify production deployment** run and the live item card before treating this merge as verified in production.

The current card gap is the four +2 skill bonuses and granted skill. Their canonical names are known from the baseline, but the catalog lacks source-backed skill/localization/controller lookups. Resume with those lookups; after the Black Matriarch baseline is complete, return to the Phase 2 snapshot upload/ownership contract before starting PostgreSQL implementation.

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
- Repository Actions variables are set: `GAME_LAB_AUTO_DEPLOY=true` and `GAME_LAB_BASE_URL` set to the production HTTPS origin.
- PR #13 merged as `7d2e95f`. Its validation and image publishing passed; the VPS deployed it; **Verify production deployment** passed the live API version check and production smoke tests.
- The user checked the live catalog and confirmed **“Only show highest-level version”** works for Monster Infrequents and Legendaries.
- Use the ordinary PR review/merge path for future changes. Keep the timer enabled. Troubleshooting commands are in [PULL-DEPLOY.md](PULL-DEPLOY.md).


## Session 4 completed — October 26, 2026

- PR #15 merged as `319e530`; all required checks passed. The updated observability releases were explicitly deployed from the VPS. Grafana remains private.
- The **Game Lab Overview** dashboard is visible under **Dashboards → Game Lab**. It shows API request rate, p95 response time, and 5xx percentage; the screenshot showed active `/api` traffic, approximately 4.7 ms p95, and 0% 5xx at that time.
- Loki returned API pod logs, including successful 200 requests to `/api`, the catalog, and item search.
- Tempo returned a `GET /api/grim-dawn/items` trace with six spans: the HTTP request, two HTTP send spans, one SQLite `PRAGMA`, and two SQLite `SELECT` spans. The SQLite spans appear under the same request trace, confirming correlation.
- Metrics, logs, traces, and database-span correlation are verified end to end.

## Latest item-card progress — October 26, 2026

- PR #21 merged as `391688b` (`Show GrimTools stat ranges on item cards`).
- The API calculates minimum and maximum rolls for variable equipment properties and includes `retaliation…` stats. Web labels now map the Black Matriarch’s familiar stats to Cunning, Health, Vitality Resistance, Pierce Resistance, and Acid Retaliation.
- Its source `offensiveSlowPoisonMin` and duration fields render together as `70/95 Poison Damage over 5 Seconds`.
- The five item-card unit tests and the Validate plus Build application images workflows passed before merge.
- Still missing from the rendered card: `+2 Cadence`, `+2 Curse of Frailty`, `+2 Nidalla’s Hidden Hand`, `+2 Righteous Fervor`, and the granted skill **Venom of the Black Matriarch** with its effect. These need reusable source data, not item-specific hard-coded names.
- The four canonical baseline cards remain the acceptance set: [ITEM-CARD-BASELINE.md](ITEM-CARD-BASELINE.md). For this chunk, compare the Black Matriarch against its GrimTools reference after confirming the production deployment.

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

1. Check the merge commit’s **Verify production deployment** result, then compare the live Black Matriarch card with its canonical GrimTools reference.
2. Add source-backed skill/localization/controller lookup data and render the four skill bonuses plus granted-skill effect; keep the four canonical cards as regressions.
3. Once the card baseline is complete, define the personal character/stash snapshot upload and ownership contract.
4. Review current VPS capacity and plan PostgreSQL persistence after the snapshot contract is agreed.
5. Keep Datadog deferred until there is a meaningful workload and repeatable failure scenarios to compare; keep phone Grafana access deferred until after the Datadog trial.

## Current caveats

- No PostgreSQL-backed personal inventory or snapshot import is implemented yet.
- Black Matriarch skill bonuses and its granted-skill effect are not yet resolved on the card; source-backed lookup data is the next item-card chunk.
- Production verification for PR #21 has not yet been recorded in this handoff.
- Grafana remains private; access uses the documented VPS port-forward and Windows SSH tunnel.
- Phone Grafana access remains deferred until after the Datadog trial.
