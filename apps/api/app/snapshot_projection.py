"""Build a strict, privacy-safe preview from gd-edit parsed maps.

The parser returns a large map containing local paths, file UUIDs, block
metadata, and save fields that the preview does not need. These helpers return
only the fields explicitly allowlisted below. They do not expose an HTTP route,
write to disk, or modify save data.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from typing import Any


class SnapshotProjectionError(ValueError):
    """The parser output is malformed or outside the supported projection."""


ITEM_TEXT_FIELDS = {
    "itemRecordPath": "basename",
    "prefixRecord": "prefix-name",
    "suffixRecord": "suffix-name",
    "modifierRecord": "modifier-name",
    "transmuteRecord": "transmute-name",
    "relicRecord": "relic-name",
    "relicBonus": "relic-bonus",
    "augmentRecord": "augment-name",
    "augmentBonus": "augment-bonus",
    "ascendedRecord": "ascended-name",
    "ascendedBonus": "ascended-bonus",
}
ITEM_INT_FIELDS = {
    "stackCount": ("stack-count", 1),
    "seed": ("seed", 0),
    "relicSeed": ("relic-seed", 0),
    "relicCompletionLevel": ("relic-completion-level", 0),
    "augmentSeed": ("augment-seed", 0),
    "seedRerollCount": ("seed-reroll-count", 0),
    "affixRerollCount": ("affix-reroll-count", 0),
}


def _mapping(value: Any, field: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise SnapshotProjectionError(f"{field} must be an object")
    return value


def _sequence(value: Any, field: str) -> Sequence[Any]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise SnapshotProjectionError(f"{field} must be an array")
    return value


def _integer(value: Any, field: str, *, minimum: int = 0) -> int:
    if type(value) is not int or value < minimum:
        raise SnapshotProjectionError(f"{field} must be an integer >= {minimum}")
    return value


def _text(value: Any, field: str, *, required: bool = False) -> str | None:
    if value is None or value == "":
        if required:
            raise SnapshotProjectionError(f"{field} must be a non-empty string")
        return None
    if not isinstance(value, str) or len(value) > 512:
        raise SnapshotProjectionError(f"{field} must be a string of at most 512 characters")
    return value


def _coordinate(value: Any, field: str) -> int | float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SnapshotProjectionError(f"{field} must be numeric")
    if not math.isfinite(value):
        raise SnapshotProjectionError(f"{field} must be finite")
    return value


def _project_item(raw: Any, location: dict[str, Any]) -> dict[str, Any] | None:
    item = _mapping(raw, "item")
    path = _text(item.get("basename"), "item.basename")
    # Empty item slots are represented by records with no basename.
    if path is None:
        return None

    projected: dict[str, Any] = {
        "itemRecordPath": _text(item.get("basename"), "item.basename", required=True),
        "location": location,
    }
    for output_name, input_name in ITEM_TEXT_FIELDS.items():
        if output_name == "itemRecordPath":
            continue
        value = _text(item.get(input_name), f"item.{input_name}")
        if value is not None:
            projected[output_name] = value

    for output_name, (input_name, minimum) in ITEM_INT_FIELDS.items():
        value = item.get(input_name)
        if value is not None:
            projected[output_name] = _integer(
                value,
                f"item.{input_name}",
                minimum=minimum,
            )

    for input_name, output_name in (("X", "x"), ("Y", "y")):
        if input_name in item:
            projected[output_name] = _coordinate(item[input_name], f"item.{input_name}")
    return projected


def _project_items(items: Any, location: dict[str, Any]) -> list[dict[str, Any]]:
    result = []
    for raw in _sequence(items, "items"):
        item = _project_item(raw, location)
        if item is not None:
            result.append(item)
    return result


def project_character(parsed: Mapping[str, Any]) -> dict[str, Any]:
    """Allowlist the character header and item instances from a gd-edit map."""
    parsed = _mapping(parsed, "character")
    file_info = _mapping(parsed.get("meta-fileinfo"), "character.meta-fileinfo")
    character = {
        "name": _text(parsed.get("character-name"), "character-name", required=True),
        "level": _integer(parsed.get("character-level"), "character-level", minimum=1),
        "hardcore": parsed.get("hardcore-mode"),
    }
    if type(character["hardcore"]) is not bool:
        raise SnapshotProjectionError("hardcore-mode must be a boolean")

    items: list[dict[str, Any]] = []
    for index, raw in enumerate(_sequence(parsed.get("equipment"), "equipment")):
        item = _project_item(raw, {"type": "equipped", "slotIndex": index})
        if item is not None:
            items.append(item)

    for sack_index, sack_raw in enumerate(
        _sequence(parsed.get("inventory-sacks"), "inventory-sacks")
    ):
        sack = _mapping(sack_raw, "inventory sack")
        for item in _project_items(
            sack.get("inventory-items"),
            {"type": "carried", "sackIndex": sack_index},
        ):
            items.append(item)

    for tab_index, tab_raw in enumerate(_sequence(parsed.get("stashes"), "stashes")):
        tab = _mapping(tab_raw, "personal stash tab")
        for item in _project_items(
            tab.get("items"),
            {"type": "personalStash", "tabIndex": tab_index},
        ):
            items.append(item)

    return {
        "sourceType": "character",
        "formatVersion": _integer(
            file_info.get("data-version"),
            "character.meta-fileinfo.data-version",
            minimum=1,
        ),
        "character": character,
        "items": items,
    }


def project_shared_stash(parsed: Mapping[str, Any]) -> dict[str, Any]:
    """Allowlist shared-stash item instances; omit paths, tab labels, and headers."""
    parsed = _mapping(parsed, "shared stash")
    tabs = _sequence(parsed.get("stash"), "shared stash.stash")
    items: list[dict[str, Any]] = []
    for tab_index, tab_raw in enumerate(tabs):
        tab = _mapping(tab_raw, "shared stash tab")
        for item in _project_items(
            tab.get("inventory-items"),
            {"type": "sharedStash", "tabIndex": tab_index},
        ):
            items.append(item)

    return {
        "sourceType": "sharedStash",
        "formatVersion": _integer(
            parsed.get("version"),
            "shared stash.version",
            minimum=1,
        ),
        "items": items,
    }
