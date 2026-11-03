"""Run the gd-edit read-only parser in a bounded subprocess."""

from __future__ import annotations

import json
import os
import subprocess
import tempfile
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from .snapshot_projection import (
    SnapshotProjectionError,
    project_character,
    project_shared_stash,
)


MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_OUTPUT_BYTES = 16 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 15
DEFAULT_JVM_HEAP = "384m"
SUPPORTED_SOURCE_TYPES = {"character", "sharedStash"}


class SnapshotParserError(ValueError):
    """The parser could not safely read or project a save file."""


class SnapshotParser:
    """Parse save bytes through the bundled gd-edit JAR without persisting them.

    The caller supplies the Java executable, gd-edit standalone JAR, and the
    directory containing the read-only Clojure worker source. Each call writes
    an ephemeral input copy, starts a fresh JVM, captures output without
    logging it, projects only allowlisted fields, then removes the temp file.
    """

    def __init__(
        self,
        *,
        java_executable: str | Path,
        parser_jar: str | Path,
        worker_source_dir: str | Path,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        max_input_bytes: int = MAX_INPUT_BYTES,
        max_output_bytes: int = MAX_OUTPUT_BYTES,
        jvm_heap: str = DEFAULT_JVM_HEAP,
    ) -> None:
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if max_input_bytes <= 0 or max_output_bytes <= 0:
            raise ValueError("byte limits must be positive")
        self.java_executable = str(java_executable)
        self.parser_jar = str(Path(parser_jar))
        self.worker_source_dir = str(Path(worker_source_dir))
        self.timeout_seconds = timeout_seconds
        self.max_input_bytes = max_input_bytes
        self.max_output_bytes = max_output_bytes
        self.jvm_heap = jvm_heap

    def parse_bytes(self, source_type: str, payload: bytes) -> dict[str, Any]:
        """Return a minimal preview for one character or shared-stash file."""
        if source_type not in SUPPORTED_SOURCE_TYPES:
            raise SnapshotParserError("Unsupported save-file type")
        if not isinstance(payload, bytes):
            raise SnapshotParserError("Save-file payload must be bytes")
        if not payload:
            raise SnapshotParserError("Save file is empty")
        if len(payload) > self.max_input_bytes:
            raise SnapshotParserError("Save file exceeds the size limit")

        suffix = ".gdc" if source_type == "character" else ".gst"
        try:
            with tempfile.TemporaryDirectory(prefix="game-lab-snapshot-") as temp_dir:
                input_path = Path(temp_dir) / f"input{suffix}"
                with input_path.open("xb") as temp_file:
                    temp_file.write(payload)
                input_path.chmod(0o600)

                classpath = os.pathsep.join(
                    (self.parser_jar, self.worker_source_dir)
                )
                command = [
                    self.java_executable,
                    "-Xms32m",
                    f"-Xmx{self.jvm_heap}",
                    "-Djna.nosys=true",
                    "--enable-native-access=ALL-UNNAMED",
                    "-cp",
                    classpath,
                    "clojure.main",
                    "-m",
                    "game-lab.snapshot-worker",
                    source_type,
                    str(input_path),
                ]
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="strict",
                    timeout=self.timeout_seconds,
                    check=False,
                )
        except subprocess.TimeoutExpired:
            raise SnapshotParserError("Save parsing exceeded the time limit") from None
        except (OSError, UnicodeError):
            raise SnapshotParserError("Read-only parser could not be started") from None

        if completed.returncode != 0:
            # The child's stderr may contain user paths or parser internals.
            raise SnapshotParserError("Save file is invalid or unsupported")
        if len(completed.stdout.encode("utf-8")) > self.max_output_bytes:
            raise SnapshotParserError("Parsed result exceeds the size limit")

        try:
            parsed = json.loads(completed.stdout)
            if not isinstance(parsed, Mapping):
                raise SnapshotParserError("Parser returned an invalid result")
            if source_type == "character":
                return project_character(parsed)
            return project_shared_stash(parsed)
        except (json.JSONDecodeError, SnapshotProjectionError) as error:
            raise SnapshotParserError("Parser returned an invalid result") from None
