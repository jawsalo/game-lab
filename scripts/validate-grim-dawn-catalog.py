#!/usr/bin/env python3
"""Validate vendored Grim Dawn catalog databases and their provenance."""

from __future__ import annotations

import base64
import gzip
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


def validate_skill_lookup(manifest: dict[str, object], directory: Path) -> None:
    lookup = manifest.get("skillLookup")
    if not isinstance(lookup, dict):
        fail(f"{directory.relative_to(ROOT)}: skill lookup provenance is missing")

    filename = require(lookup.get("file"), str, "skillLookup.file")
    if Path(filename).name != filename:
        fail(f"{directory.relative_to(ROOT)}: skillLookup.file must be a filename")
    if lookup.get("encoding") != "base64+gzip":
        fail(f"{directory.relative_to(ROOT)}: unsupported skill lookup encoding")

    expected_bytes = require(lookup.get("bytes"), int, "skillLookup.bytes")
    expected_blob_sha = require(lookup.get("gitBlobSha"), str, "skillLookup.gitBlobSha")
    skill_path = directory / filename
    if not skill_path.is_file():
        fail(f"{skill_path.relative_to(ROOT)}: generated skill lookup not found")

    contents = skill_path.read_bytes()
    if len(contents) != expected_bytes:
        fail(f"{skill_path.relative_to(ROOT)}: skill lookup size mismatch")
    git_blob = hashlib.sha1(
        f"blob {len(contents)}".encode("ascii") + b"\0" + contents
    ).hexdigest()
    if git_blob != expected_blob_sha:
        fail(f"{skill_path.relative_to(ROOT)}: skill lookup blob checksum mismatch")

    try:
        decoded = base64.b64decode(contents.strip(), validate=True)
        data = json.loads(gzip.decompress(decoded))
    except (ValueError, OSError, gzip.BadGzipFile, json.JSONDecodeError) as error:
        fail(f"{skill_path.relative_to(ROOT)}: cannot decode skill lookup: {error}")

    if data.get("schemaVersion") != lookup.get("schemaVersion"):
        fail(f"{skill_path.relative_to(ROOT)}: skill schema version mismatch")
    if data.get("gameVersion") != manifest.get("gameVersion"):
        fail(f"{skill_path.relative_to(ROOT)}: skill game version mismatch")
    if data.get("itemCount") != manifest.get("recordCount"):
        fail(f"{skill_path.relative_to(ROOT)}: skill item count mismatch")
    items = data.get("items")
    if not isinstance(items, dict) or len(items) != data.get("resolvedItemCount"):
        fail(f"{skill_path.relative_to(ROOT)}: invalid resolved item map")
    if data.get("unresolvedSkillReferences") != []:
        fail(f"{skill_path.relative_to(ROOT)}: unresolved skill references remain")
    if data.get("source") != lookup.get("sourceHashes"):
        fail(f"{skill_path.relative_to(ROOT)}: skill source hashes mismatch")

    canonical = items.get("it9040")
    if not isinstance(canonical, dict):
        fail(f"{skill_path.relative_to(ROOT)}: canonical it9040 skill data is missing")
    bonuses = canonical.get("skillBonuses")
    expected_bonuses = [
        ("Cadence", 2),
        ("Curse of Frailty", 2),
        ("Nidalla's Hidden Hand", 2),
        ("Righteous Fervor", 2),
    ]
    actual_bonuses = [
        (entry.get("name"), entry.get("ranks"))
        for entry in bonuses or []
        if isinstance(entry, dict)
    ]
    if actual_bonuses != expected_bonuses:
        fail(f"{skill_path.relative_to(ROOT)}: canonical skill bonuses mismatch")

    granted = canonical.get("grantedSkills")
    if not isinstance(granted, list) or len(granted) != 1:
        fail(f"{skill_path.relative_to(ROOT)}: canonical granted skill mismatch")
    proc = granted[0]
    proc_properties = proc.get("properties")
    if (
        proc.get("name") != "Venom of the Black Matriarch"
        or proc.get("description")
        != "Inject your target with the deadly venom of the Black Matriarch."
        or proc.get("chanceToRun") != 15
        or proc.get("triggerType") != "AttackEnemy"
        or not isinstance(proc_properties, dict)
        or proc_properties.get("skillCooldownTime") != 0.5
        or proc_properties.get("skillActiveDuration") != 5
        or proc_properties.get("offensiveSlowPoisonMin") != [102, 112]
        or proc_properties.get("defensivePhysical") != -10
    ):
        fail(f"{skill_path.relative_to(ROOT)}: canonical granted-skill effects mismatch")


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

    validate_skill_lookup(manifest, path.parent)

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
