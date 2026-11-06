#!/usr/bin/env python3
"""Build a local JSONL index of Grim Dawn item DBRs and resolved tag fields.

The source game export and output are expected to remain outside the repository.
This tool is intentionally read-only with respect to the extracted game data.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable


MAIN_LAYERS = ("base", "gdx1", "gdx2", "gdx3")
LOCALIZED_FIELDS = ("FileDescription", "itemNameTag", "description", "itemText")


def read_game_text(path: Path) -> str:
    """Decode common ArchiveTool text encodings without silently losing accents."""
    raw = path.read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):
        return raw.decode("utf-16")
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def parse_dbr(path: Path) -> dict[str, list[str]]:
    """Parse ArchiveTool's key,value, rows, preserving repeated fields."""
    fields: dict[str, list[str]] = defaultdict(list)
    from io import StringIO

    for row in csv.reader(StringIO(read_game_text(path), newline="")):
        if len(row) < 2:
            continue
        key = row[0].strip()
        if not key:
            continue
        values = row[1:]
        if values and values[-1] == "":  # ArchiveTool emits a final delimiter.
            values = values[:-1]
        fields[key].append(",".join(values))
    return dict(fields)


def parse_localization_file(path: Path) -> dict[str, set[str]]:
    """Read Grim Dawn key=value localization rows; ignore comments and blanks."""
    entries: dict[str, set[str]] = defaultdict(set)
    for line in read_game_text(path).splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        if key:
            entries[key].add(value.strip())
    return dict(entries)


def load_localizations(layer_paths: Iterable[tuple[str, Path]]) -> tuple[dict[str, dict[str, set[str]]], Counter[str]]:
    localizations: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    counts: Counter[str] = Counter()
    for layer, root in layer_paths:
        if not root.is_dir():
            raise ValueError(f"Localization directory does not exist for layer {layer}: {root}")
        for path in sorted(root.rglob("*.txt")):
            parsed = parse_localization_file(path)
            for key, values in parsed.items():
                localizations[layer][key].update(values)
            counts[layer] += len(parsed)
    return {layer: dict(tags) for layer, tags in localizations.items()}, counts


def parse_layer_arg(value: str) -> tuple[str, Path]:
    layer, separator, raw_path = value.partition("=")
    layer = layer.strip().lower()
    if not separator or not layer or not raw_path:
        raise argparse.ArgumentTypeError("use LAYER=PATH, for example base=C:\\GD-Data-Export\\text_en")
    return layer, Path(raw_path.strip()).expanduser()


def discover_record_roots(database_root: Path) -> list[tuple[str, Path]]:
    roots: list[tuple[str, Path]] = []
    base = database_root / "database" / "records"
    if base.is_dir():
        roots.append(("base", base))
    mods = database_root / "mods"
    if mods.is_dir():
        for mod in sorted(p for p in mods.iterdir() if p.is_dir()):
            records = mod / "database" / "records"
            if records.is_dir():
                roots.append((mod.name.lower(), records))
    if not roots:
        raise ValueError(f"No database\\records roots found under {database_root}")
    return roots


def localization_fallbacks(layer: str) -> list[str]:
    if layer in MAIN_LAYERS:
        index = MAIN_LAYERS.index(layer)
        return [layer, *reversed(MAIN_LAYERS[:index])]
    if layer == "survivalmode":
        return ["survivalmode", "base"]
    if layer == "survivalmode1":
        return ["survivalmode1", "survivalmode", "base"]
    if layer == "survivalmode2":
        return ["survivalmode2", "survivalmode1", "survivalmode", "base"]
    return [layer, "base"]


def resolve_value(value: str, layer: str, localizations: dict[str, dict[str, set[str]]]) -> dict[str, object]:
    """Resolve an exact localization key through the layer's fallback chain."""
    for candidate_layer in localization_fallbacks(layer):
        choices = localizations.get(candidate_layer, {}).get(value)
        if choices:
            sorted_choices = sorted(choices)
            if len(sorted_choices) == 1:
                return {"value": sorted_choices[0], "resolved_layer": candidate_layer, "status": "resolved"}
            return {"value": sorted_choices, "resolved_layer": candidate_layer, "status": "ambiguous"}
    status = "unresolved" if value.startswith("tag") else "literal"
    return {"value": value, "resolved_layer": None, "status": status}


def record_output(layer: str, record_path: str, fields: dict[str, list[str]], localizations: dict[str, dict[str, set[str]]]) -> dict[str, object]:
    localized: dict[str, list[dict[str, object]]] = {}
    for field in LOCALIZED_FIELDS:
        if field in fields:
            localized[field] = [resolve_value(value, layer, localizations) for value in fields[field]]
    return {
        "source_layer": layer,
        "record_path": record_path,
        "class": fields.get("Class", []),
        "fields": fields,
        "localized_fields": localized,
    }


def build_index(database_root: Path, localization_layers: list[tuple[str, Path]], output: Path, overwrite: bool = False) -> dict[str, object]:
    if output.exists() and not overwrite:
        raise FileExistsError(f"Output already exists; pass --overwrite to replace it: {output}")
    if output.resolve().is_relative_to(database_root.resolve()):
        raise ValueError("Output must be outside the extracted database tree")
    roots = discover_record_roots(database_root)
    localizations, localization_counts = load_localizations(localization_layers)
    output.parent.mkdir(parents=True, exist_ok=True)
    total_dbrs: Counter[str] = Counter()
    item_records: Counter[str] = Counter()
    class_counts: Counter[str] = Counter()
    localization_statuses: Counter[str] = Counter()

    with output.open("w", encoding="utf-8", newline="\n") as stream:
        for layer, records_root in roots:
            for path in sorted(records_root.rglob("*.dbr")):
                total_dbrs[layer] += 1
                relative = path.relative_to(records_root).as_posix()
                if not relative.lower().startswith("items/"):
                    continue
                fields = parse_dbr(path)
                document = record_output(layer, "records/" + relative, fields, localizations)
                stream.write(json.dumps(document, ensure_ascii=False, sort_keys=True) + "\n")
                item_records[layer] += 1
                for item_class in fields.get("Class", []):
                    class_counts[item_class] += 1
                localization_statuses.update(
                    result["status"]
                    for values in document["localized_fields"].values()
                    for result in values
                )

    return {
        "dbr_roots": {layer: str(root) for layer, root in roots},
        "total_dbrs_by_layer": dict(sorted(total_dbrs.items())),
        "item_records_by_layer": dict(sorted(item_records.items())),
        "total_dbrs": sum(total_dbrs.values()),
        "item_records": sum(item_records.values()),
        "localization_entries_by_layer": dict(sorted(localization_counts.items())),
        "localized_field_statuses": dict(sorted(localization_statuses.items())),
        "top_classes": class_counts.most_common(20),
        "output": str(output),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database-root", required=True, type=Path, help="Combined AssetManager-Work folder")
    parser.add_argument("--text-layer", action="append", default=[], type=parse_layer_arg, metavar="LAYER=PATH", help="Extracted text_en directory; repeat per layer")
    parser.add_argument("--output", required=True, type=Path, help="Local JSONL output path outside the repository")
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output file")
    args = parser.parse_args(argv)
    try:
        summary = build_index(args.database_root, args.text_layer, args.output, args.overwrite)
    except (OSError, ValueError, csv.Error) as error:
        print(f"Index failed: {error}", file=sys.stderr)
        return 2
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
