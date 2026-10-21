# Game Lab V9 — Session 3 Handoff

**Date:** October 21, 2026  
**Repository:** `jawsalo/game-lab`  
**Roadmap:** [ROADMAP-V9.md](ROADMAP-V9.md)

## Stopping point

The open-source observability stack is deployed. The user reached Grafana, signed in with username `admin`, and chose to stop before building dashboards. Prometheus is receiving Game Lab API metrics. This is a clean stopping point; the next work can start in Grafana without repeating the infrastructure setup.

## Verified

- Prometheus, Grafana, Loki, Tempo, and Alloy are running in namespace `observability`.
- Grafana is private and is not exposed through the public ingress.
- Grafana was opened locally using a Kubernetes port-forward on the VPS and an SSH tunnel from the user's Windows PC.
- API requests were found in Prometheus under metric `http_server_duration_milliseconds_count`.
- Confirmed route series for `/api`, `/api/grim-dawn/catalog`, and `/api/grim-dawn/items`, each labeled `job="game-lab-api"`, `http_status_code="200"`, with three requests recorded at query time.
- The instrumented API deploy passed the public smoke test. A transient 502 line appeared during one deployment output, but the retrying smoke test completed successfully.
- Alloy's remote-write endpoint was corrected from port 9090 to the Prometheus Service port 80; Alloy was upgraded and restarted. Application metrics are subsequently visible in Prometheus.

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

## Next session

1. **Make Grafana understandable:** create a small Game Lab dashboard with request rate, response latency, and error rate. Start with the Prometheus data source already receiving API metrics; confirm its name in Grafana before building panels.
2. **Verify the other signals:** use Grafana Explore to find Game Lab logs in Loki, then check whether API traces are visible in Tempo. Record any missing configuration before changing it.
3. **Return to Phase 2:** define the character/stash snapshot upload and ownership contract before implementing PostgreSQL persistence or parsing.
4. **Keep Datadog deferred** until there is a meaningful workload and repeatable failure scenarios to compare.

## Current caveats

- A friendly Game Lab dashboard has not been created.
- Prometheus metrics are verified. Logs and traces are deployed as part of the stack but have not yet been confirmed through the user's Grafana workflow.
- No PostgreSQL-backed personal inventory or snapshot import is implemented yet.
- Do not expose Grafana publicly as part of dashboard setup.
