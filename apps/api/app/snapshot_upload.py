"""Authenticated, bounded, temporary-only save-file preview endpoint."""

from __future__ import annotations

import asyncio
import json
import os
import threading
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.datastructures import FormData, UploadFile
from starlette.responses import JSONResponse

from .auth import require_owner_write
from .snapshot_parser import (
    MAX_INPUT_BYTES,
    MAX_OUTPUT_BYTES,
    SnapshotParser,
    SnapshotParserError,
)

MAX_UPLOAD_FILES = 2
MAX_REQUEST_BYTES = 32 * 1024 * 1024 + 64 * 1024
MAX_PREVIEW_BYTES = MAX_OUTPUT_BYTES
MAX_UPLOAD_FIELD_NAMES = {"characterFile", "sharedStashFile", "sharedStashMode"}

router = APIRouter(prefix="/api/snapshots", tags=["snapshots"])
_preview_semaphore = asyncio.Semaphore(1)
_parser_semaphore = threading.BoundedSemaphore(1)


def _configured_parser() -> SnapshotParser:
    """Load parser paths only when preview is explicitly enabled."""
    if os.getenv("GAME_LAB_SNAPSHOT_PREVIEW_ENABLED", "").lower() != "true":
        raise HTTPException(
            status_code=503,
            detail="Save preview is disabled",
        )
    java = os.getenv("GAME_LAB_JAVA_EXECUTABLE", "")
    jar = os.getenv("GAME_LAB_PARSER_JAR", "")
    worker = os.getenv("GAME_LAB_PARSER_WORKER_SOURCE", "")
    if not java or not jar or not worker:
        raise HTTPException(
            status_code=503,
            detail="Save preview is unavailable until the parser runtime is installed",
        )
    if not Path(java).is_file() or not Path(jar).is_file() or not Path(worker).is_dir():
        raise HTTPException(
            status_code=503,
            detail="Save preview parser runtime is unavailable",
        )
    try:
        return SnapshotParser(
            java_executable=java,
            parser_jar=jar,
            worker_source_dir=worker,
        )
    except ValueError:
        raise HTTPException(
            status_code=503,
            detail="Save preview parser runtime is unavailable",
        ) from None


class RequestBodyLimitMiddleware:
    """Enforce the upload request limit while multipart data is being read."""

    def __init__(self, app: Any, *, max_bytes: int = MAX_REQUEST_BYTES) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: dict[str, Any], receive: Any, send: Any) -> None:
        if not (
            scope.get("type") == "http"
            and scope.get("method") == "POST"
            and scope.get("path") == "/api/snapshots/preview"
        ):
            await self.app(scope, receive, send)
            return

        content_length = next(
            (
                value
                for key, value in scope.get("headers", [])
                if key.lower() == b"content-length"
            ),
            None,
        )
        if content_length is not None:
            try:
                declared_length = int(content_length)
            except ValueError:
                await JSONResponse(
                    {"detail": "Invalid request size"}, status_code=400
                )(scope, receive, send)
                return
            if declared_length < 0 or declared_length > self.max_bytes:
                await JSONResponse(
                    {"detail": "Upload request exceeds the size limit"},
                    status_code=413,
                )(scope, receive, send)
                return

        received = 0

        async def limited_receive() -> dict[str, Any]:
            nonlocal received
            message = await receive()
            if message.get("type") == "http.request":
                received += len(message.get("body", b""))
                if received > self.max_bytes:
                    raise _RequestBodyTooLarge
            return message

        try:
            await self.app(scope, limited_receive, send)
        except _RequestBodyTooLarge:
            await JSONResponse(
                {"detail": "Upload request exceeds the size limit"},
                status_code=413,
            )(scope, receive, send)


class _RequestBodyTooLarge(Exception):
    """Raised when a streamed request exceeds the upload boundary."""


class _ParserBusy(Exception):
    """Raised when another save is currently consuming the parser slot."""


def _parse_bytes_in_slot(
    parser: SnapshotParser, source_type: str, payload: bytes
) -> dict[str, Any]:
    if not _parser_semaphore.acquire(blocking=False):
        raise _ParserBusy
    try:
        return parser.parse_bytes(source_type, payload)
    finally:
        _parser_semaphore.release()


def _validate_form(
    form: FormData,
) -> tuple[UploadFile | None, UploadFile | None, str | None]:
    """Accept at most one explicitly selected character and stash file."""
    pairs = list(form.multi_items())
    if any(name not in MAX_UPLOAD_FIELD_NAMES for name, _ in pairs):
        raise HTTPException(status_code=422, detail="Unsupported upload field")

    character_values = form.getlist("characterFile")
    stash_values = form.getlist("sharedStashFile")
    mode_values = form.getlist("sharedStashMode")
    if len(character_values) > 1 or len(stash_values) > 1 or len(mode_values) > 1:
        raise HTTPException(status_code=422, detail="Duplicate upload field")
    if len(character_values) + len(stash_values) > MAX_UPLOAD_FILES:
        raise HTTPException(status_code=422, detail="Too many save files")

    character = character_values[0] if character_values else None
    stash = stash_values[0] if stash_values else None
    if character is None and stash is None:
        raise HTTPException(status_code=422, detail="Select a character or stash file")
    if character is not None and not isinstance(character, UploadFile):
        raise HTTPException(status_code=422, detail="Character upload must be a file")
    if stash is not None and not isinstance(stash, UploadFile):
        raise HTTPException(status_code=422, detail="Stash upload must be a file")

    mode = mode_values[0] if mode_values else None
    if stash is not None and mode not in {"softcore", "hardcore"}:
        raise HTTPException(
            status_code=422,
            detail="Choose whether the shared stash is softcore or hardcore",
        )
    if stash is None and mode is not None:
        raise HTTPException(status_code=422, detail="Stash mode requires a stash file")
    return character, stash, mode if isinstance(mode, str) else None


async def _read_limited(upload: UploadFile) -> bytes:
    payload = await upload.read(MAX_INPUT_BYTES + 1)
    if not payload:
        raise HTTPException(status_code=422, detail="Save file is empty")
    if len(payload) > MAX_INPUT_BYTES:
        raise HTTPException(status_code=413, detail="Save file exceeds the size limit")
    return payload


async def _parse_file(
    parser: SnapshotParser,
    source_type: str,
    upload: UploadFile,
    *,
    stash_mode: str | None = None,
) -> dict[str, Any]:
    payload = await _read_limited(upload)
    try:
        parsed = await asyncio.to_thread(
            _parse_bytes_in_slot, parser, source_type, payload
        )
    except _ParserBusy:
        raise HTTPException(
            status_code=429,
            detail="Another save preview is currently running; retry shortly",
            headers={"Retry-After": "5"},
        ) from None
    except SnapshotParserError as error:
        raise HTTPException(status_code=422, detail=str(error)) from None

    result: dict[str, Any] = {
        "sourceType": source_type,
        "formatVersion": parsed["formatVersion"],
        "itemCount": len(parsed["items"]),
        "items": parsed["items"],
    }
    if source_type == "character":
        result["character"] = parsed["character"]
    elif stash_mode is not None:
        result["stashMode"] = stash_mode
    return result


@router.post("/preview")
async def preview_snapshot(
    request: Request,
    _: dict[str, Any] = Depends(require_owner_write),
) -> dict[str, Any]:
    """Parse the selected save files in a temporary workspace without storing them."""
    parser = _configured_parser()
    content_type = request.headers.get("content-type", "").lower()
    if not content_type.startswith("multipart/form-data"):
        raise HTTPException(status_code=415, detail="Use a multipart save-file upload")

    async with _preview_semaphore:
        try:
            async with request.form(
                max_files=MAX_UPLOAD_FILES,
                max_fields=1,
                max_part_size=1024,
            ) as form:
                character, stash, stash_mode = _validate_form(form)
                results: list[dict[str, Any]] = []
                if character is not None:
                    results.append(await _parse_file(parser, "character", character))
                if stash is not None:
                    results.append(
                        await _parse_file(
                            parser,
                            "sharedStash",
                            stash,
                            stash_mode=stash_mode,
                        )
                    )
        except HTTPException:
            raise
        except Exception:
            # Do not expose parser, multipart, temporary path, or file details.
            raise HTTPException(
                status_code=422,
                detail="Upload could not be parsed as a supported save file",
            ) from None

    preview = {"files": results, "itemCount": sum(row["itemCount"] for row in results)}
    if len(json.dumps(preview, ensure_ascii=False).encode("utf-8")) > MAX_PREVIEW_BYTES:
        raise HTTPException(status_code=413, detail="Save preview exceeds the response size limit")
    return preview
