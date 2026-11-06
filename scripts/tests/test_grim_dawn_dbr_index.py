"""Tests for the read-only local Grim Dawn DBR indexer."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.index_grim_dawn_dbrs import build_index, parse_dbr, read_game_text, resolve_value


class GrimDawnDbrIndexTests(unittest.TestCase):
    def test_archive_tool_rows_preserve_values_and_duplicate_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "sample.dbr"
            path.write_text(
                'FileDescription,Sample Name,\nitemText,"A line, with a comma.",\nClass,QuestItem,\nClass,OtherClass,\n',
                encoding="utf-8",
            )
            fields = parse_dbr(path)
        self.assertEqual(fields["FileDescription"], ["Sample Name"])
        self.assertEqual(fields["itemText"], ["A line, with a comma."])
        self.assertEqual(fields["Class"], ["QuestItem", "OtherClass"])

    def test_localization_uses_layer_then_parent_fallback_and_keeps_conflicts(self) -> None:
        tags = {
            "base": {"shared": {"Base value"}, "conflict": {"One", "Two"}},
            "gdx1": {"shared": {"Expansion value"}},
        }
        self.assertEqual(resolve_value("shared", "gdx1", tags)["value"], "Expansion value")
        self.assertEqual(resolve_value("conflict", "gdx1", tags)["status"], "ambiguous")
        self.assertEqual(resolve_value("tagMissing", "gdx1", tags)["status"], "unresolved")

    def test_build_index_emits_layered_item_records_and_localized_fields(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            temp_root = Path(temp)
            root = temp_root / "db"
            base_record = root / "database" / "records" / "items" / "sample.dbr"
            gdx3_record = root / "mods" / "gdx3" / "database" / "records" / "items" / "sample.dbr"
            base_text = root / "texts" / "base" / "text_en"
            gdx3_text = root / "texts" / "gdx3" / "text_en"
            for path in (base_record, gdx3_record):
                path.parent.mkdir(parents=True, exist_ok=True)
            base_text.mkdir(parents=True)
            gdx3_text.mkdir(parents=True)
            base_record.write_text("Class,WeaponMelee_Sword,\nFileDescription,Base Sword,\n", encoding="utf-8")
            gdx3_record.write_text("Class,WeaponMelee_Sword,\nitemNameTag,tagSword,\nitemLevel,94,\n", encoding="utf-8")
            (base_text / "tags_items.txt").write_text("tagSword=Base Name\n", encoding="utf-8")
            (gdx3_text / "tagsgdx3_items.txt").write_text("tagSword=GDX3 Name\n", encoding="utf-8")
            output = temp_root / "out" / "index.jsonl"

            summary = build_index(root, [("base", base_text), ("gdx3", gdx3_text)], output)
            records = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(summary["total_dbrs"], 2)
        self.assertEqual(summary["item_records"], 2)
        gdx3 = next(record for record in records if record["source_layer"] == "gdx3")
        self.assertEqual(gdx3["record_path"], "records/items/sample.dbr")
        self.assertEqual(gdx3["localized_fields"]["itemNameTag"][0]["value"], "GDX3 Name")

    def test_game_text_falls_back_to_windows_1252(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "accent.txt"
            path.write_bytes("tagName=Beronath’s Horn\n".encode("cp1252"))
            self.assertEqual(read_game_text(path), "tagName=Beronath’s Horn\n")


if __name__ == "__main__":
    unittest.main()
