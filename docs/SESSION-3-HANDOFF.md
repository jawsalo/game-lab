# Game Lab V9 — Session 3 Handoff

**Updated:** October 26, 2026  
**Repository:** `jawsalo/game-lab`  
**Roadmap:** [ROADMAP-V9.md](ROADMAP-V9.md)

## Stopping point

The phone-approved PR-to-VPS path is live and has completed production deployments. The **“Only show highest-level version”** catalog option was verified for Monster Infrequents and Legendaries. Grafana metrics, Loki logs, Tempo traces, and SQLite span correlation are also verified end to end.

Item-card fidelity is complete for this checkpoint. PR #23 added source-backed skill data for the Black Matriarch’s four +2 skill bonuses and Venom of the Black Matriarch proc. PR #24 put offensive properties before defensive properties. PR #25 replaced the raw `offensiveFireMin` label with “Fire Damage” for both item stats and granted-skill effects.

The user verified the updated cards on the live site and is happy with them. Production API version is `d581b26`. Keep the four cards in [ITEM-CARD-BASELINE.md](ITEM-CARD-BASELINE.md) as the regression set; the card milestone is done for now.

The next feature is personal character/stash snapshot upload. Define the upload, ownership, privacy, and snapshot-version contract before implementing persistence.

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

## Item-card milestone complete — October 26, 2026

- PRs #17–21 delivered Mythical naming, duplicate-description removal, character/resistance labels, and GrimTools-style stat ranges.
- PR #23 added source-backed skill lookups and the Black Matriarch’s four skill bonuses and granted proc.
- PR #24 ordered properties with offensive stats before defensive stats.
- PR #25 labels flat fire damage as “Fire Damage” on item properties and granted-skill effects.
- Production API version `d581b26` is live. The user checked the live cards and is happy with the result.
- The four canonical cards in [ITEM-CARD-BASELINE.md](ITEM-CARD-BASELINE.md) remain the regression set. No further item-card work is currently queued.

## Next feature — personal snapshots

1. Define the snapshot upload and ownership contract: accepted export, identity, privacy, version/history behavior, and separation from shared catalog data.
2. Check current VPS capacity and plan PostgreSQL persistence before changing production.
3. Implement a small read-only upload/parse/preview slice, then expand to owned-item lookup, duplicates, and roll comparisons.
4. Use the resulting workload for repeatable traffic and failure exercises; defer the Datadog trial until those are ready.
5. Keep controlled MCP operations as a later, separately scoped track.

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

1. Item-card fidelity is complete for this checkpoint; the user is happy with the live cards. PR #23–25 are merged, with production at `d581b26`.
2. Define the personal character/stash snapshot upload and ownership contract.
3. Review current VPS capacity and plan PostgreSQL persistence after the contract is agreed.
4. Implement a small read-only upload/parse/preview slice before expanding inventory features.
5. Use the resulting workload for repeatable traffic and failure scenarios, then compare Datadog with the open-source stack. Keep phone Grafana access deferred until after the Datadog trial.

## Current caveats

- No PostgreSQL-backed personal inventory or snapshot import is implemented yet.
- No further item-card defect is currently queued; the user accepted the live card presentation. The four canonical cards remain the regression set.
- Grafana remains private; access uses the documented VPS port-forward and Windows SSH tunnel.
- Phone Grafana access remains deferred until after the Datadog trial.
