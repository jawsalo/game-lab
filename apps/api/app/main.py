"""Game Lab HTTP API."""

import os

from fastapi import FastAPI

SERVICE_NAME = "game-lab-api"
ENVIRONMENT = os.getenv("APP_ENV", "development")
VERSION = os.getenv("APP_VERSION", "dev")

app = FastAPI(
    title="Game Lab API",
    version=VERSION,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
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
async def readiness() -> dict[str, str]:
    """Confirm that the API is ready to serve requests."""
    return {"status": "ready", "service": SERVICE_NAME}
