#!/usr/bin/env python3
"""Compare a local DBR index with the pinned catalog and report candidates.

This is an evidence report, not an automatic crosswalk publisher. It writes a
local JSONL file and never changes the source index or SQLite catalog.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


NAME_FIELDS = ("FileDescription", "itemNameTag", "description")
DISCRIMINATORS = ("item_level", "level_requirement", "rarity", "bitmap")
STAT_FIELD_PREFIXES = ("offensive", "defensive", "character", "conversion", "armor")


def number(value: Any) -> int | float | None:
    if value is None or value == "":
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return int(parsed) if parsed.is_integer() else parsed


def normalize_name(value: Any) -> str:
    if not isinstance(value, str):
        return ""
    value = unicodedata.normalize("NFKC", value).casefold()
    value = re.sub(r"\^[a-z]", "", value)
    value = value.strip().strip('"').strip()
    return " ".join(re.findall(r"[\w]+", value, flags=re.UNICODE))


def normalize_bitmap(value: Any) -> str:
    if not isinstance(value, str) or not value.strip():
        return ""
    value = value.strip().replace("\\", "/").casefold()
    value = re.sub(r"\.(?:tex|png)$", "", value)
    return value


def first(fields: dict[str, list[str]], key: str) -> str | None:
    values = fields.get(key, [])
    return values[0].strip() if values and values[0].strip() else None


def localized_names(record: dict[str, Any]) -> list[str]:
    localized = record.get("localized_fields", {})
    names: list[str] = []
    for field in NAME_FIELDS:
        for result in localized.get(field, []):
            value = result.get("value")
            if result.get("status") in ("resolved", "literal") and isinstance(value, str):
                value = value.strip().strip('"').strip()
                if value and value not in names:
                    names.append(value)
    return names


def load_catalog(path: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    uri = f"{path.resolve().as_uri()}?mode=ro&immutable=1"
    try:
        connection = sqlite3.connect(uri, uri=True)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        metadata = dict(connection.execute("SELECT key, value FROM metadata"))
        columns = {row[1] for row in connection.execute("PRAGMA table_info(items)")}
        required = {
            "id", "name", "category", "rarity", "level_requirement",
            "item_level", "bitmap", "name_tag", "record_json",
        }
        missing = required - columns
        if missing:
            raise ValueError(f"Catalog schema is missing expected columns: {sorted(missing)}")
        rows = connection.execute(
            """SELECT id, name, category, rarity, level_requirement,
                      item_level, bitmap, name_tag, record_json
               FROM items ORDER BY id"""
        ).fetchall()
    except sqlite3.Error as error:
        raise ValueError(f"Cannot read catalog SQLite: {error}") from error
    finally:
        if "connection" in locals():
            connection.close()
    items = []
    for row in rows:
        item = dict(row)
        try:
            parsed_record = json.loads(item.pop("record_json"))
        except (TypeError, json.JSONDecodeError) as error:
            raise ValueError(f"Catalog item {item.get('id')} has invalid record_json") from error
        item["record"] = parsed_record if isinstance(parsed_record, dict) else {}
        items.append(item)
    return items, metadata


def read_index(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Invalid JSONL at line {line_number}: {error}") from error


def shared_discriminator_evidence(record: dict[str, Any], item: dict[str, Any]) -> tuple[list[str], list[str], list[str]]:
    fields = record.get("fields", {})
    source_values = {
        "item_level": number(first(fields, "itemLevel")),
        "level_requirement": number(first(fields, "levelRequirement")),
        "rarity": first(fields, "itemClassification"),
        "bitmap": first(fields, "bitmap"),
    }
    catalog_values = {
        "item_level": number(item.get("item_level")),
        "level_requirement": number(item.get("level_requirement")),
        "rarity": item.get("rarity"),
        "bitmap": item.get("bitmap"),
    }
    matched: list[str] = []
    mismatched: list[str] = []
    unavailable: list[str] = []
    for key in DISCRIMINATORS:
        source = source_values[key]
        catalog = catalog_values[key]
        if source is None or catalog is None:
            unavailable.append(key)
            continue
        if key == "rarity":
            equal = str(source).casefold() == str(catalog).casefold()
        elif key == "bitmap":
            equal = normalize_bitmap(source) == normalize_bitmap(catalog)
        else:
            equal = source == catalog
        (matched if equal else mismatched).append(key)
    return matched, mismatched, unavailable


def record_stat_evidence(record: dict[str, Any], item: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Compare numeric item stats that both raw record sources actually contain."""
    source_fields = record.get("fields", {})
    catalog_record = item.get("record", {})

    def is_stat_field(key: str) -> bool:
        return key.startswith(STAT_FIELD_PREFIXES)

    source_stats = {}
    for key, values in source_fields.items():
        if not is_stat_field(key):
            continue
        value = number(first(source_fields, key))
        if value is not None:
            source_stats[key] = value

    catalog_stats = {}
    for key, value in catalog_record.items():
        if not is_stat_field(key):
            continue
        parsed = number(value)
        if parsed is not None:
            catalog_stats[key] = parsed

    matched = []
    mismatched = []
    for key in sorted(source_stats.keys() & catalog_stats.keys()):
        if source_stats[key] == catalog_stats[key]:
            # Zero values help reject a different damage type when both datasets
            # explicitly include the field, but are not useful positive evidence.
            if source_stats[key] != 0:
                matched.append(key)
        else:
            mismatched.append(key)
    return matched, mismatched


def make_candidates(record: dict[str, Any], category_index: dict[str, list[dict[str, Any]]]) -> dict[str, Any] | None:
    classes = [value for value in record.get("class", []) if value in category_index]
    if not classes:
        return None
    fields = record.get("fields", {})
    raw_name_tag = first(fields, "itemNameTag")
    names = localized_names(record)
    candidates: list[dict[str, Any]] = []
    method = "unmatched"

    if raw_name_tag:
        tag_pool = [
            item
            for category in classes
            for item in category_index[category]
            if item.get("name_tag") == raw_name_tag
        ]
        if tag_pool:
            tag_matches = []
            for item in tag_pool:
                matched, mismatched, unavailable = shared_discriminator_evidence(record, item)
                matched_stats, mismatched_stats = record_stat_evidence(record, item)
                if not mismatched and not mismatched_stats:
                    tag_matches.append((item, matched, unavailable, matched_stats))
            if tag_matches:
                method = "exact_name_tag"
                candidates = [
                    {
                        "id": item["id"],
                        "name": item["name"],
                        "category": item["category"],
                        "matched_discriminators": matched,
                        "unavailable_discriminators": unavailable,
                        "matched_record_stats": matched_stats,
                    }
                    for item, matched, unavailable, matched_stats in tag_matches
                ]

    if not candidates:
        name_keys = {normalize_name(name) for name in names if normalize_name(name)}
        if name_keys:
            name_matches = []
            for category in classes:
                for item in category_index[category]:
                    if normalize_name(item.get("name")) not in name_keys:
                        continue
                    matched, mismatched, _ = shared_discriminator_evidence(record, item)
                    matched_stats, mismatched_stats = record_stat_evidence(record, item)
                    # Require at least one independent supporting field; never map on name alone.
                    if not mismatched and not mismatched_stats and (matched or matched_stats):
                        name_matches.append((item, matched, matched_stats))
            if name_matches:
                method = "display_name_composite"
                candidates = [
                    {
                        "id": item["id"],
                        "name": item["name"],
                        "category": item["category"],
                        "matched_discriminators": matched,
                        "matched_record_stats": matched_stats,
                    }
                    for item, matched, matched_stats in name_matches
                ]

    status = "unique" if len(candidates) == 1 else "ambiguous" if candidates else "unmatched"
    return {
        "source_layer": record.get("source_layer"),
        "record_path": record.get("record_path"),
        "class": classes,
        "item_name_tag": raw_name_tag,
        "source_names": names,
        "status": status,
        "method": method,
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


def build_report(index_path: Path, catalog_path: Path, output_path: Path, overwrite: bool = False) -> dict[str, Any]:
    if output_path.exists() and not overwrite:
        raise FileExistsError(f"Output already exists; pass --overwrite to replace it: {output_path}")
    if output_path.resolve() == index_path.resolve():
        raise ValueError("Candidate report cannot overwrite its source DBR index")
    if output_path.resolve() == catalog_path.resolve():
        raise ValueError("Candidate report cannot overwrite the pinned catalog")
    catalog_items, metadata = load_catalog(catalog_path)
    if metadata.get("game_version") != "1.3.1.0":
        raise ValueError(f"Expected catalog game_version 1.3.1.0, got {metadata.get('game_version')!r}")
    category_index: dict[str, list[dict[str, Any]]] = {}
    for item in catalog_items:
        category_index.setdefault(item.get("category"), []).append(item)

    statuses: Counter[str] = Counter()
    methods: Counter[str] = Counter()
    by_layer: dict[str, Counter[str]] = {}
    by_class: dict[str, Counter[str]] = {}
    eligible = 0
    total_index_records = 0
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8", newline="\n") as stream:
        for record in read_index(index_path):
            total_index_records += 1
            result = make_candidates(record, category_index)
            if result is None:
                continue
            eligible += 1
            statuses[result["status"]] += 1
            methods[result["method"]] += 1
            layer = result["source_layer"] or "unknown"
            by_layer.setdefault(layer, Counter())[result["status"]] += 1
            for item_class in result["class"]:
                by_class.setdefault(item_class, Counter())[result["status"]] += 1
            stream.write(json.dumps(result, ensure_ascii=False, sort_keys=True) + "\n")

    return {
        "catalog_game_version": metadata.get("game_version"),
        "catalog_record_count": len(catalog_items),
        "index_item_records": total_index_records,
        "catalog_category_records": eligible,
        "status_counts": dict(sorted(statuses.items())),
        "method_counts": dict(sorted(methods.items())),
        "by_layer": {key: dict(sorted(value.items())) for key, value in sorted(by_layer.items())},
        "by_class": {key: dict(sorted(value.items())) for key, value in sorted(by_class.items())},
        "output": str(output_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", required=True, type=Path, help="Local JSONL output from index_grim_dawn_dbrs.py")
    parser.add_argument("--catalog-sqlite", required=True, type=Path, help="Pinned 1.3.1.0 items.sqlite")
    parser.add_argument("--output", required=True, type=Path, help="Local candidate report JSONL output")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing candidate report")
    args = parser.parse_args(argv)
    try:
        summary = build_report(args.index, args.catalog_sqlite, args.output, args.overwrite)
    except (OSError, ValueError, sqlite3.Error) as error:
        print(f"Candidate report failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
