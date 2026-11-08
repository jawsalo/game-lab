"""Tests for single-owner cookie authentication and CSRF protection."""

from __future__ import annotations

import os
import unittest
from http.cookies import SimpleCookie
from unittest.mock import patch

from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import Response

from apps.api.app.auth import (
    SESSION_COOKIE_NAME,
    SESSION_MAX_AGE_SECONDS,
    LoginRequest,
    _create_session,
    _read_session,
    login,
    logout,
    require_owner,
    require_owner_write,
    session_status,
)


class OwnerAuthenticationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.environment = patch.dict(
            os.environ,
            {
                "GAME_LAB_OWNER_PASSWORD": "test-owner-password",
                "GAME_LAB_SESSION_SECRET": "s" * 48,
            },
            clear=False,
        )
        self.environment.start()
        self.addCleanup(self.environment.stop)

    @staticmethod
    def request(cookie: str | None = None, csrf: str | None = None) -> Request:
        headers: list[tuple[bytes, bytes]] = []
        if cookie is not None:
            headers.append((b"cookie", f"{SESSION_COOKIE_NAME}={cookie}".encode()))
        if csrf is not None:
            headers.append((b"x-csrf-token", csrf.encode()))
        return Request(
            {
                "type": "http",
                "http_version": "1.1",
                "method": "GET",
                "scheme": "https",
                "path": "/api/auth/session",
                "raw_path": b"/api/auth/session",
                "query_string": b"",
                "root_path": "",
                "headers": headers,
                "server": ("game-lab.test", 443),
                "client": ("127.0.0.1", 12345),
            }
        )

    def login_and_get_session(self) -> tuple[str, str]:
        response = Response()
        result = login(LoginRequest(password="test-owner-password"), response)
        self.assertEqual(result, {"authenticated": True})
        cookie_header = response.headers["set-cookie"]
        parsed_cookie = SimpleCookie()
        parsed_cookie.load(cookie_header)
        cookie_value = parsed_cookie[SESSION_COOKIE_NAME].value
        parsed = _read_session(cookie_value, b"s" * 48)
        assert parsed is not None
        return cookie_value, parsed["csrf"]

    def test_login_sets_secure_http_only_cookie_and_session_exposes_csrf(self) -> None:
        response = Response()
        result = login(LoginRequest(password="test-owner-password"), response)

        self.assertEqual(result, {"authenticated": True})
        cookie = response.headers["set-cookie"].lower()
        self.assertIn(f"{SESSION_COOKIE_NAME}=", cookie)
        self.assertIn("httponly", cookie)
        self.assertIn("secure", cookie)
        self.assertIn("samesite=strict", cookie)
        self.assertIn("path=/api", cookie)

        cookie_value, csrf = self.login_and_get_session()
        session = session_status(self.request(cookie_value))
        self.assertTrue(session["authenticated"])
        self.assertEqual(session["csrfToken"], csrf)
        self.assertEqual(require_owner(self.request(cookie_value))["sub"], "owner")

    def test_wrong_password_and_oversized_password_are_rejected(self) -> None:
        for wrong_password in ("wrong", "mot de passe🔒"):
            with self.subTest(password=wrong_password):
                with self.assertRaises(HTTPException) as raised:
                    login(LoginRequest(password=wrong_password), Response())
                self.assertEqual(raised.exception.status_code, 401)
        with self.assertRaises(ValueError):
            LoginRequest(password="x" * 257)
        with self.assertRaises(HTTPException) as raised:
            require_owner(self.request())
        self.assertEqual(raised.exception.status_code, 401)

    def test_writes_require_csrf_and_logout_clears_cookie(self) -> None:
        cookie_value, csrf = self.login_and_get_session()
        with self.assertRaises(HTTPException) as raised:
            require_owner_write(self.request(cookie_value), require_owner(self.request(cookie_value)))
        self.assertEqual(raised.exception.status_code, 403)

        session = require_owner(self.request(cookie_value))
        authorized_request = self.request(cookie_value, csrf)
        self.assertEqual(require_owner_write(authorized_request, session)["sub"], "owner")

        response = Response()
        result = logout(response, session)
        self.assertEqual(result, {"authenticated": False})
        self.assertIn("max-age=0", response.headers["set-cookie"].lower())

    def test_missing_configuration_fails_closed(self) -> None:
        with patch.dict(
            os.environ,
            {"GAME_LAB_OWNER_PASSWORD": "", "GAME_LAB_SESSION_SECRET": ""},
        ):
            with self.assertRaises(HTTPException) as raised:
                login(LoginRequest(password="anything"), Response())
        self.assertEqual(raised.exception.status_code, 503)

    def test_signed_sessions_reject_tampering_and_expiry(self) -> None:
        secret = b"k" * 48
        token, _ = _create_session(secret, now=100)

        session = _read_session(token, secret, now=100)
        self.assertEqual(session["exp"], 100 + SESSION_MAX_AGE_SECONDS)  # type: ignore[index]
        self.assertIsNone(_read_session(token + "x", secret, now=100))
        self.assertIsNone(
            _read_session(token, secret, now=100 + SESSION_MAX_AGE_SECONDS)
        )


if __name__ == "__main__":
    unittest.main()
