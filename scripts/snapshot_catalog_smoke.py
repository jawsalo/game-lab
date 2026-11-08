#!/usr/bin/env python3
"""Parse local Grim Dawn saves and summarize DBR-to-catalog resolution."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from apps.api.app.snapshot_parser import SnapshotParser  # noqa: E402


DEFAULT_LAYER_PRIORITY = ("gdx3", "gdx2", "gdx1", "base")
STATUSES = ("unique", "ambiguous", "unmatched", "missing")


def normalize_path(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    return value.replace("\\", "/").strip("/").casefold()


def load_candidate_report(path: Path) -> dict[str, list[dict[str, Any]]]:
    by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
    with path.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as error:
                raise ValueError(f"Candidate report has invalid JSON at line {line_number}") from error
            if not isinstance(row, dict):
                continue
            key = normalize_path(row.get("record_path"))
            if key:
                by_path[key].append(row)
    return by_path


def resolve_path(
    rows: list[dict[str, Any]], layer_priority: tuple[str, ...]
) -> tuple[str, str | None]:
    """Use the highest-priority matching game layer; never guess among IDs."""
    if not rows:
        return "missing", None

    rank = {layer: index for index, layer in enumerate(layer_priority)}
    available_layers = {
        str(row.get("source_layer") or "base").casefold() for row in rows
    }
    selected_layer = min(
        available_layers,
        key=lambda layer: (rank.get(layer, len(rank)), layer),
    )
    selected = [
        row
        for row in rows
        if str(row.get("source_layer") or "base").casefold() == selected_layer
    ]

    ids = {
        str(candidate.get("id"))
        for row in selected
        for candidate in row.get("candidates", [])
        if isinstance(candidate, dict) and candidate.get("id") is not None
    }
    row_statuses = {str(row.get("status", "unmatched")) for row in selected}
    if len(ids) > 1 or "ambiguous" in row_statuses:
        return "ambiguous", selected_layer
    if len(ids) == 1 and row_statuses == {"unique"}:
        return "unique", selected_layer
    return "unmatched", selected_layer


def summarize_items(
    parsed: dict[str, Any],
    candidate_index: dict[str, list[dict[str, Any]]],
    layer_priority: tuple[str, ...],
) -> dict[str, Any]:
    items = parsed.get("items")
    if not isinstance(items, list):
        raise ValueError("Parser result has no item list")

    statuses: Counter[str] = Counter()
    paths: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("Parser returned an invalid item")
        key = normalize_path(item.get("itemRecordPath"))
        if key is None:
            raise ValueError("Parser returned an item without a DBR path")
        status, layer = resolve_path(candidate_index.get(key, []), layer_priority)
        statuses[status] += 1
        entry = paths.setdefault(
            key,
            {"path": item["itemRecordPath"], "status": status, "sourceLayer": layer, "instances": 0},
        )
        entry["instances"] += 1
        if entry["status"] != status:
            entry["status"] = "ambiguous"

    unique_paths = len(paths)
    return {
        "formatVersion": parsed["formatVersion"],
        "itemInstances": len(items),
        "uniqueDBRPaths": unique_paths,
        "countsByStatus": {status: statuses.get(status, 0) for status in STATUSES},
        "unresolvedPaths": sorted(
            (entry for entry in paths.values() if entry["status"] != "unique"),
            key=lambda entry: (entry["status"], entry["path"].casefold()),
        ),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--java-executable", required=True, type=Path)
    parser.add_argument("--parser-jar", required=True, type=Path)
    parser.add_argument("--candidate-report", required=True, type=Path)
    parser.add_argument("--character-save", required=True, type=Path)
    parser.add_argument("--shared-stash", required=True, type=Path)
    parser.add_argument(
        "--layer-priority",
        default=",".join(DEFAULT_LAYER_PRIORITY),
        help="Highest-priority layer first; defaults to gdx3,gdx2,gdx1,base",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    layer_priority = tuple(
        part.strip().casefold() for part in args.layer_priority.split(",") if part.strip()
    )
    if not layer_priority:
        print("Snapshot check failed: layer priority is empty", file=sys.stderr)
        return 2

    try:
        candidate_index = load_candidate_report(args.candidate_report)
        parser = SnapshotParser(
            java_executable=args.java_executable,
            parser_jar=args.parser_jar,
            worker_source_dir=ROOT / "apps/parser-worker/src",
        )
        character = parser.parse_bytes("character", args.character_save.read_bytes())
        stash = parser.parse_bytes("sharedStash", args.shared_stash.read_bytes())
        result = {
            "character": summarize_items(character, candidate_index, layer_priority),
            "sharedStash": summarize_items(stash, candidate_index, layer_priority),
            "candidatePaths": len(candidate_index),
            "layerPriority": list(layer_priority),
        }
    except (OSError, ValueError, KeyError, TypeError):
        # Avoid exposing personal file paths or parser internals in diagnostics.
        print("Snapshot check failed; verify the local inputs and parser runtime.", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
