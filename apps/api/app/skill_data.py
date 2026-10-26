"""Version-pinned, source-derived Grim Dawn skill display data."""

from __future__ import annotations

import base64
import gzip
import hashlib
import json
from functools import lru_cache
from pathlib import Path
from typing import Any

DATA_DIRECTORY = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "grim-dawn"
    / "1.3.1.0"
)
LOOKUP_FILENAME = "item-skills.json.gz.b64"


class SkillDataUnavailableError(RuntimeError):
    """Raised when the versioned skill lookup cannot be verified or read."""


def _git_blob_sha1(contents: bytes) -> str:
    header = f"blob {len(contents)}\\0".encode("ascii")
    return hashlib.sha1(header + contents).hexdigest()


@lru_cache(maxsize=1)
def _load_skill_data() -> dict[str, Any]:
    provenance_path = DATA_DIRECTORY / "provenance.json"
    lookup_path = DATA_DIRECTORY / LOOKUP_FILENAME
    try:
        provenance = json.loads(provenance_path.read_text(encoding="utf-8"))
        lookup_provenance = provenance["skillLookup"]
        contents = lookup_path.read_bytes()
    except (OSError, KeyError, json.JSONDecodeError) as error:
        raise SkillDataUnavailableError("pinned skill lookup is unavailable") from error

    if lookup_provenance.get("file") != LOOKUP_FILENAME:
        raise SkillDataUnavailableError("skill lookup filename does not match provenance")
    if lookup_provenance.get("encoding") != "base64+gzip":
        raise SkillDataUnavailableError("skill lookup encoding is unsupported")
    if len(contents) != lookup_provenance.get("bytes"):
        raise SkillDataUnavailableError("skill lookup size does not match provenance")
    if _git_blob_sha1(contents) != lookup_provenance.get("gitBlobSha"):
        raise SkillDataUnavailableError("skill lookup checksum does not match provenance")

    try:
        encoded = base64.b64decode(contents.strip(), validate=True)
        data = json.loads(gzip.decompress(encoded))
    except (ValueError, OSError, gzip.BadGzipFile, json.JSONDecodeError) as error:
        raise SkillDataUnavailableError("skill lookup data is invalid") from error

    if (
        data.get("schemaVersion") != lookup_provenance.get("schemaVersion")
        or data.get("gameVersion") != provenance.get("gameVersion")
        or data.get("itemCount") != provenance.get("recordCount")
        or not isinstance(data.get("items"), dict)
        or len(data["items"]) != data.get("resolvedItemCount")
        or data.get("source") != lookup_provenance.get("sourceHashes")
    ):
        raise SkillDataUnavailableError("skill lookup identity does not match provenance")

    return data


def skill_data_for_item(item_id: str) -> dict[str, Any]:
    """Return resolved skill names and source properties for one item."""
    return _load_skill_data()["items"].get(
        item_id,
        {"skillBonuses": [], "grantedSkills": []},
    )
