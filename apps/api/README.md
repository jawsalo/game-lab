# API app

The FastAPI service exposes platform health and game-specific routes through the same-origin `/api` prefix. It uses injected runtime configuration and Kubernetes service discovery rather than fixed public URLs.

## System routes

- `GET /api`
- `GET /api/health/live`
- `GET /api/health/ready`
- `GET /api/docs`
- `GET /api/openapi.json`

Readiness includes the required Grim Dawn catalog identity and row-count check.

## Grim Dawn catalog routes

- `GET /api/grim-dawn/catalog`
- `GET /api/grim-dawn/items`
- `GET /api/grim-dawn/items/{id}`

The catalog connection uses SQLite URI `mode=ro&immutable=1` and query-only connections. The default packaged database path can be overridden with `GRIM_DAWN_DATABASE_PATH` for controlled testing or deployment variants.

Run repository validation and API regression tests from the repository root:

```bash
make validate
```
