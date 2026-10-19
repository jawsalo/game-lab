#!/usr/bin/env python3
"""Validate vendored Grim Dawn catalog databases and their provenance."""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_ROOT = ROOT / "apps" / "api" / "data" / "grim-dawn"
APPLICATION_ID = 0x47444C42
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")


def fail(message: str) -> None:
    raise SystemExit(f"Catalog validation failed: {message}")


def require(value: object, expected: type, label: str) -> object:
    if not isinstance(value, expected) or isinstance(value, bool):
        fail(f"{label} must be {expected.__name__}")
    return value


def validate_manifest(path: Path) -> None:
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"{path.relative_to(ROOT)}: cannot read provenance: {error}")

    version = path.parent.name
    schema_version = require(manifest.get("schemaVersion"), int, "schemaVersion")
    game_version = require(manifest.get("gameVersion"), str, "gameVersion")
    record_count = require(manifest.get("recordCount"), int, "recordCount")
    source_repository = require(
        manifest.get("sourceRepository"), str, "sourceRepository"
    )
    source_commit = require(manifest.get("sourceCommit"), str, "sourceCommit")
    source_path = require(manifest.get("sourcePath"), str, "sourcePath")
    database = require(manifest.get("database"), dict, "database")

    if game_version != version:
        fail(f"{path.relative_to(ROOT)}: gameVersion must match its directory")
    if schema_version != 1 or record_count <= 0:
        fail(f"{path.relative_to(ROOT)}: unsupported schema or record count")
    if not source_repository or not source_path or not COMMIT_RE.fullmatch(source_commit):
        fail(f"{path.relative_to(ROOT)}: invalid source provenance")

    filename = require(database.get("file"), str, "database.file")
    expected_bytes = require(database.get("bytes"), int, "database.bytes")
    expected_sha256 = require(database.get("sha256"), str, "database.sha256")
    if Path(filename).name != filename:
        fail(f"{path.relative_to(ROOT)}: database.file must be a filename")
    if expected_bytes <= 0 or not SHA256_RE.fullmatch(expected_sha256):
        fail(f"{path.relative_to(ROOT)}: invalid database size or SHA-256")

    database_path = path.parent / filename
    if not database_path.is_file():
        fail(f"{database_path.relative_to(ROOT)}: file not found")

    contents = database_path.read_bytes()
    actual_sha256 = hashlib.sha256(contents).hexdigest()
    if len(contents) != expected_bytes:
        fail(
            f"{database_path.relative_to(ROOT)}: expected {expected_bytes} bytes, "
            f"found {len(contents)}"
        )
    if actual_sha256 != expected_sha256:
        fail(f"{database_path.relative_to(ROOT)}: SHA-256 mismatch")

    uri = f"{database_path.resolve().as_uri()}?mode=ro&immutable=1"
    connection = sqlite3.connect(uri, uri=True)
    try:
        connection.execute("PRAGMA query_only = ON")
        application_id = connection.execute("PRAGMA application_id").fetchone()[0]
        user_version = connection.execute("PRAGMA user_version").fetchone()[0]
        integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
        metadata = dict(connection.execute("SELECT key, value FROM metadata"))
        item_count = connection.execute("SELECT COUNT(*) FROM items").fetchone()[0]
        fts_count = connection.execute("SELECT COUNT(*) FROM items_fts").fetchone()[0]
    except sqlite3.Error as error:
        fail(f"{database_path.relative_to(ROOT)}: SQLite validation failed: {error}")
    finally:
        connection.close()

    if application_id != APPLICATION_ID:
        fail(f"{database_path.relative_to(ROOT)}: application_id mismatch")
    if user_version != schema_version:
        fail(f"{database_path.relative_to(ROOT)}: schema version mismatch")
    if integrity != "ok":
        fail(f"{database_path.relative_to(ROOT)}: integrity check returned {integrity}")
    if metadata.get("game_version") != version:
        fail(f"{database_path.relative_to(ROOT)}: embedded game version mismatch")
    if metadata.get("record_count") != str(record_count):
        fail(f"{database_path.relative_to(ROOT)}: embedded record count mismatch")
    if item_count != record_count or fts_count != record_count:
        fail(
            f"{database_path.relative_to(ROOT)}: expected {record_count} rows, "
            f"found items={item_count}, FTS={fts_count}"
        )

    print(
        f"Validated Grim Dawn {version}: {record_count} items, "
        f"{expected_bytes} bytes, SHA-256 {expected_sha256}."
    )


def main() -> None:
    manifests = sorted(CATALOG_ROOT.glob("*/provenance.json"))
    if not manifests:
        fail(f"{CATALOG_ROOT.relative_to(ROOT)}: no provenance files found")
    for manifest in manifests:
        validate_manifest(manifest)


if __name__ == "__main__":
    main()
