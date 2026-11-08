"""Single-owner authentication for private Game Lab APIs."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from collections.abc import Mapping
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response
from pydantic import BaseModel, Field

SESSION_COOKIE_NAME = "game_lab_owner_session"
SESSION_MAX_AGE_SECONDS = 12 * 60 * 60
MIN_SESSION_SECRET_BYTES = 32

router = APIRouter(prefix="/api/auth", tags=["owner authentication"])


class LoginRequest(BaseModel):
    owner_password: str = Field(alias="password", max_length=256)


def _configuration() -> tuple[str, bytes]:
    password = os.getenv("GAME_LAB_OWNER_PASSWORD", "")
    secret = os.getenv("GAME_LAB_SESSION_SECRET", "").encode("utf-8")
    if not password or len(secret) < MIN_SESSION_SECRET_BYTES:
        raise HTTPException(
            status_code=503,
            detail="Owner authentication is not configured",
        )
    return password, secret


def _b64encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _sign(payload: str, secret: bytes) -> str:
    return _b64encode(hmac.new(secret, payload.encode("ascii"), hashlib.sha256).digest())


def _create_session(secret: bytes, now: int | None = None) -> tuple[str, str]:
    issued_at = int(time.time() if now is None else now)
    csrf_token = secrets.token_urlsafe(32)
    payload = _b64encode(
        json.dumps(
            {
                "sub": "owner",
                "iat": issued_at,
                "exp": issued_at + SESSION_MAX_AGE_SECONDS,
                "csrf": csrf_token,
            },
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")
    )
    return f"{payload}.{_sign(payload, secret)}", csrf_token


def _read_session(token: str | None, secret: bytes, now: int | None = None) -> dict[str, Any] | None:
    if not token or token.count(".") != 1:
        return None
    payload, signature = token.split(".", 1)
    if not hmac.compare_digest(signature, _sign(payload, secret)):
        return None
    try:
        value = json.loads(_b64decode(payload))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        return None
    current_time = int(time.time() if now is None else now)
    if (
        not isinstance(value, Mapping)
        or value.get("sub") != "owner"
        or not isinstance(value.get("exp"), int)
        or value["exp"] <= current_time
        or not isinstance(value.get("csrf"), str)
    ):
        return None
    return dict(value)


def require_owner(request: Request) -> dict[str, Any]:
    """Reject requests without a valid signed owner session."""
    _, secret = _configuration()
    session = _read_session(request.cookies.get(SESSION_COOKIE_NAME), secret)
    if session is None:
        raise HTTPException(status_code=401, detail="Authentication required")
    return session


def require_owner_write(
    request: Request,
    session: dict[str, Any] = Depends(require_owner),
) -> dict[str, Any]:
    """Require a matching CSRF header for cookie-authenticated writes."""
    csrf_header = request.headers.get("x-csrf-token", "")
    if not hmac.compare_digest(csrf_header, session["csrf"]):
        raise HTTPException(status_code=403, detail="CSRF validation failed")
    return session


@router.post("/login")
def login(credentials: LoginRequest, response: Response) -> dict[str, bool]:
    """Exchange the configured owner password for a short-lived session."""
    expected_password, secret = _configuration()
    if not hmac.compare_digest(
        credentials.owner_password.encode("utf-8"), expected_password.encode("utf-8")
    ):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token, _ = _create_session(secret)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=SESSION_MAX_AGE_SECONDS,
        httponly=True,
        secure=True,
        samesite="strict",
        path="/api",
    )
    return {"authenticated": True}


@router.get("/session")
def session_status(request: Request) -> dict[str, Any]:
    """Return owner session state and the CSRF token for same-origin writes."""
    _, secret = _configuration()
    current = _read_session(request.cookies.get(SESSION_COOKIE_NAME), secret)
    if current is None:
        return {"authenticated": False}
    return {"authenticated": True, "csrfToken": current["csrf"]}


@router.post("/logout")
def logout(
    response: Response,
    _: dict[str, Any] = Depends(require_owner_write),
) -> dict[str, bool]:
    """Invalidate the browser's owner session cookie."""
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/api",
        secure=True,
        httponly=True,
        samesite="strict",
    )
    return {"authenticated": False}
