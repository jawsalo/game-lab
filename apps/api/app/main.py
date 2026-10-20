"""Game Lab HTTP API."""

import os

from fastapi import FastAPI, HTTPException

from .catalog import CatalogUnavailableError
from .grim_dawn import catalog as grim_dawn_catalog
from .grim_dawn import router as grim_dawn_router
from .telemetry import configure_telemetry, shutdown_telemetry

SERVICE_NAME = "game-lab-api"
ENVIRONMENT = os.getenv("APP_ENV", "development")
VERSION = os.getenv("APP_VERSION", "dev")

app = FastAPI(
    title="Game Lab API",
    version=VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)
app.include_router(grim_dawn_router)

telemetry_providers = configure_telemetry(app)
app.add_event_handler(
    "shutdown", lambda: shutdown_telemetry(telemetry_providers)
)


@app.get("/api", tags=["system"])
async def api_root() -> dict[str, str]:
    """Return basic service metadata."""
    return {
        "service": SERVICE_NAME,
        "environment": ENVIRONMENT,
        "version": VERSION,
    }


@app.get("/api/health/live", tags=["health"])
async def liveness() -> dict[str, str]:
    """Confirm that the API process is running."""
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/api/health/ready", tags=["health"])
def readiness() -> dict[str, str]:
    """Confirm that the API and its required catalog are ready."""
    try:
        grim_dawn_catalog.readiness()
    except CatalogUnavailableError as error:
        raise HTTPException(status_code=503, detail=str(error)) from error
    return {"status": "ready", "service": SERVICE_NAME}
