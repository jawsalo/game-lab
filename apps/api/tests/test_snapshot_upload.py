"""Tests for bounded, authenticated, temporary snapshot previews."""

from __future__ import annotations

import asyncio
import unittest
from unittest.mock import patch

from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import Response

from apps.api.app.snapshot_upload import (
    MAX_INPUT_BYTES,
    RequestBodyLimitMiddleware,
    _read_limited,
    preview_snapshot,
)


class FakeParser:
    def __init__(self) -> None:
        self.calls: list[tuple[str, bytes]] = []

    def parse_bytes(self, source_type: str, payload: bytes) -> dict[str, object]:
        self.calls.append((source_type, payload))
        if source_type == "character":
            return {
                "formatVersion": 8,
                "character": {"name": "Synthetic Hero", "level": 100, "hardcore": False},
                "items": [
                    {
                        "itemRecordPath": "records/items/example.dbr",
                        "location": {"type": "equipped", "slotIndex": 0},
                    }
                ],
            }
        return {
            "formatVersion": 11,
            "items": [
                {
                    "itemRecordPath": "records/items/stash-example.dbr",
                    "location": {"type": "sharedStash", "tabIndex": 0},
                }
            ],
        }


def _multipart_request(parts: list[tuple[str, str | None, bytes]]) -> Request:
    boundary = "game-lab-test-boundary"
    chunks: list[bytes] = []
    for name, filename, value in parts:
        chunks.append(f"--{boundary}\r\n".encode())
        if filename is None:
            chunks.append(
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode()
            )
        else:
            chunks.append(
                (
                    f'Content-Disposition: form-data; name="{name}"; '
                    f'filename="{filename}"\r\n'
                    "Content-Type: application/octet-stream\r\n\r\n"
                ).encode()
            )
        chunks.append(value)
        chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode())
    body = b"".join(chunks)
    scope = {
        "type": "http",
        "http_version": "1.1",
        "method": "POST",
        "scheme": "https",
        "path": "/api/snapshots/preview",
        "raw_path": b"/api/snapshots/preview",
        "query_string": b"",
        "root_path": "",
        "headers": [
            (b"content-type", f"multipart/form-data; boundary={boundary}".encode()),
            (b"content-length", str(len(body)).encode()),
        ],
        "server": ("game-lab.test", 443),
        "client": ("127.0.0.1", 12345),
    }
    sent = False

    async def receive() -> dict[str, object]:
        nonlocal sent
        if sent:
            return {"type": "http.disconnect"}
        sent = True
        return {"type": "http.request", "body": body, "more_body": False}

    return Request(scope, receive)


class FakeUpload:
    def __init__(self, payload: bytes) -> None:
        self.payload = payload

    async def read(self, size: int = -1) -> bytes:
        return self.payload[:size] if size >= 0 else self.payload


class SnapshotUploadTests(unittest.TestCase):
    def test_preview_parses_selected_files_and_omits_client_filenames(self) -> None:
        parser = FakeParser()
        request = _multipart_request(
            [
                ("characterFile", "C:\\private\\player.gdc", b"character-bytes"),
                ("sharedStashFile", "transfer.gsh", b"stash-bytes"),
                ("sharedStashMode", None, b"hardcore"),
            ]
        )
        with patch(
            "apps.api.app.snapshot_upload._configured_parser", return_value=parser
        ):
            result = asyncio.run(preview_snapshot(request, {"sub": "owner"}))

        self.assertEqual(result["itemCount"], 2)
        self.assertEqual(parser.calls, [
            ("character", b"character-bytes"),
            ("sharedStash", b"stash-bytes"),
        ])
        self.assertEqual(result["files"][1]["stashMode"], "hardcore")
        self.assertNotIn("player.gdc", str(result))
        self.assertNotIn("transfer.gsh", str(result))

    def test_preview_requires_explicit_stash_mode_and_rejects_empty_upload(self) -> None:
        parser = FakeParser()
        cases = (
            (
                [("sharedStashFile", "transfer.gst", b"stash-bytes")],
                "Choose whether the shared stash is softcore or hardcore",
            ),
            ([], "Select a character or stash file"),
        )
        for parts, message in cases:
            with self.subTest(message=message):
                request = _multipart_request(parts)
                with patch(
                    "apps.api.app.snapshot_upload._configured_parser",
                    return_value=parser,
                ):
                    with self.assertRaises(HTTPException) as raised:
                        asyncio.run(preview_snapshot(request, {"sub": "owner"}))
                self.assertEqual(raised.exception.status_code, 422)
                self.assertEqual(raised.exception.detail, message)

    def test_per_file_limit_is_enforced_before_parser(self) -> None:
        with self.assertRaises(HTTPException) as raised:
            asyncio.run(_read_limited(FakeUpload(b"x" * (MAX_INPUT_BYTES + 1))))  # type: ignore[arg-type]
        self.assertEqual(raised.exception.status_code, 413)

    def test_request_body_middleware_rejects_oversized_declared_length(self) -> None:
        captured: list[dict[str, object]] = []

        async def app(scope: dict[str, object], receive: object, send: object) -> None:
            self.fail("Oversized request must be rejected before reaching the route")

        middleware = RequestBodyLimitMiddleware(app, max_bytes=4)
        scope = {
            "type": "http",
            "method": "POST",
            "path": "/api/snapshots/preview",
            "headers": [(b"content-length", b"5")],
        }

        async def receive() -> dict[str, object]:
            self.fail("The body must not be read after declared-size rejection")

        async def send(message: dict[str, object]) -> None:
            captured.append(message)

        asyncio.run(middleware(scope, receive, send))  # type: ignore[arg-type]
        self.assertEqual(captured[0]["status"], 413)

    def test_request_body_middleware_caps_streamed_body_without_content_length(self) -> None:
        captured: list[dict[str, object]] = []

        async def app(scope: dict[str, object], receive: object, send: object) -> None:
            from starlette.requests import Request

            request = Request(scope, receive)  # type: ignore[arg-type]
            await request.body()

        middleware = RequestBodyLimitMiddleware(app, max_bytes=4)
        scope = {
            "type": "http",
            "http_version": "1.1",
            "method": "POST",
            "scheme": "https",
            "path": "/api/snapshots/preview",
            "raw_path": b"/api/snapshots/preview",
            "query_string": b"",
            "root_path": "",
            "headers": [],
            "server": ("game-lab.test", 443),
            "client": ("127.0.0.1", 12345),
        }
        messages = [
            {"type": "http.request", "body": b"12345", "more_body": False}
        ]

        async def receive() -> dict[str, object]:
            if messages:
                return messages.pop(0)
            return {"type": "http.disconnect"}

        async def send(message: dict[str, object]) -> None:
            captured.append(message)

        asyncio.run(middleware(scope, receive, send))  # type: ignore[arg-type]
        self.assertEqual(captured[0]["status"], 413)


if __name__ == "__main__":
    unittest.main()
