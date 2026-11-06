"""Tests for conservative DBR-to-catalog candidate matching."""

from __future__ import annotations

import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.match_grim_dawn_dbr_candidates import build_report, make_candidates


def catalog_item(
    item_id: str,
    name: str = "Mythical Test Sword",
    name_tag: str | None = "tagTestSword",
    item_level: int | None = 94,
    bitmap: str | None = "items/test_sword.png",
    record: dict[str, object] | None = None,
) -> dict[str, object]:
    return {
        "id": item_id,
        "name": name,
        "category": "WeaponMelee_Sword",
        "rarity": "Legendary",
        "level_requirement": 94,
        "item_level": item_level,
        "bitmap": bitmap,
        "name_tag": name_tag,
        "record": record or {},
    }


def dbr_record(
    name_tag: str | None = "tagTestSword",
    name: str | None = "Mythical Test Sword",
    item_level: str | None = "94.000000",
    bitmap: str | None = "items/test_sword.tex",
) -> dict[str, object]:
    fields: dict[str, list[str]] = {
        "Class": ["WeaponMelee_Sword"],
        "itemClassification": ["Legendary"],
        "levelRequirement": ["94"],
    }
    if name_tag:
        fields["itemNameTag"] = [name_tag]
    if item_level:
        fields["itemLevel"] = [item_level]
    if bitmap:
        fields["bitmap"] = [bitmap]
    localized: dict[str, list[dict[str, object]]] = {}
    if name:
        localized["FileDescription"] = [{"value": name, "status": "literal"}]
    return {
        "source_layer": "gdx3",
        "record_path": "records/items/test_sword.dbr",
        "class": ["WeaponMelee_Sword"],
        "fields": fields,
        "localized_fields": localized,
    }


def make_catalog_db(path: Path, items: list[dict[str, object]]) -> None:
    connection = sqlite3.connect(path)
    connection.executescript(
        "CREATE TABLE metadata (key TEXT, value TEXT);"
        "CREATE TABLE items (id TEXT, name TEXT, category TEXT, rarity TEXT, "
        "level_requirement INTEGER, item_level INTEGER, bitmap TEXT, name_tag TEXT, record_json TEXT);"
    )
    connection.execute("INSERT INTO metadata VALUES ('game_version', '1.3.1.0')")
    connection.execute("INSERT INTO metadata VALUES ('record_count', ?)", (str(len(items)),))
    connection.executemany(
        "INSERT INTO items VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (
                item["id"], item["name"], item["category"], item["rarity"],
                item["level_requirement"], item["item_level"], item["bitmap"], item["name_tag"],
                json.dumps(item["record"]),
            )
            for item in items
        ],
    )
    connection.commit()
    connection.close()


class DbrCandidateTests(unittest.TestCase):
    def test_exact_name_tag_and_matching_discriminators_is_unique(self) -> None:
        record = dbr_record()
        candidates = [
            catalog_item("it-one"),
            catalog_item("it-other-level", item_level=65, bitmap="items/other.png"),
        ]
        report = make_candidates(record, {"WeaponMelee_Sword": candidates})
        self.assertEqual(report["status"], "unique")
        self.assertEqual(report["method"], "exact_name_tag")
        self.assertEqual(report["candidates"][0]["id"], "it-one")

    def test_identical_tag_and_fields_remain_ambiguous(self) -> None:
        report = make_candidates(
            dbr_record(),
            {"WeaponMelee_Sword": [catalog_item("it-one"), catalog_item("it-two")]},
        )
        self.assertEqual(report["status"], "ambiguous")
        self.assertEqual(report["candidate_count"], 2)

    def test_nonzero_record_stats_disambiguate_elemental_weapon_variants(self) -> None:
        record = dbr_record()
        record["fields"]["offensiveBaseColdMin"] = ["13.000000"]
        record["fields"]["offensiveBaseColdMax"] = ["25.000000"]
        # ArchiveTool emits default-zero stat fields. Those explicit zeros let
        # us rule out a catalog variant with a different elemental damage type.
        record["fields"]["offensiveBasePoisonMin"] = ["0.000000"]
        record["fields"]["offensiveBasePoisonMax"] = ["0.000000"]
        cold = catalog_item(
            "it-cold",
            record={"offensiveBaseColdMin": 13, "offensiveBaseColdMax": 25},
        )
        poison = catalog_item(
            "it-poison",
            record={"offensiveBasePoisonMin": 13, "offensiveBasePoisonMax": 25},
        )

        report = make_candidates(record, {"WeaponMelee_Sword": [cold, poison]})

        self.assertEqual(report["status"], "unique")
        self.assertEqual(report["candidates"][0]["id"], "it-cold")
        self.assertEqual(
            report["candidates"][0]["matched_record_stats"],
            ["offensiveBaseColdMax", "offensiveBaseColdMin"],
        )

    def test_catalog_omitted_stat_is_unavailable_not_a_conflict(self) -> None:
        record = dbr_record()
        record["fields"]["characterBaseAttackSpeed"] = ["-0.020000"]
        report = make_candidates(
            record,
            {"WeaponMelee_Sword": [catalog_item("it-one")]},
        )
        self.assertEqual(report["status"], "unique")

    def test_name_fallback_requires_an_independent_matching_field(self) -> None:
        record = dbr_record(name_tag=None)
        report = make_candidates(record, {"WeaponMelee_Sword": [catalog_item("it-one", name_tag=None)]})
        self.assertEqual(report["status"], "unique")
        self.assertEqual(report["method"], "display_name_composite")

        name_only = dbr_record(name_tag=None, item_level=None, bitmap=None)
        name_only["fields"].pop("levelRequirement")
        name_only["fields"].pop("itemClassification")
        report = make_candidates(name_only, {"WeaponMelee_Sword": [catalog_item("it-one", name_tag=None, item_level=None, bitmap=None)]})
        self.assertEqual(report["status"], "unmatched")

    def test_category_mismatch_is_not_a_candidate(self) -> None:
        record = dbr_record()
        report = make_candidates(record, {"WeaponMelee_Dagger": [catalog_item("it-one")]})
        self.assertIsNone(report)

    def test_report_is_versioned_and_keeps_unmatched_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            database = root / "items.sqlite"
            index = root / "index.jsonl"
            output = root / "candidate-report.jsonl"
            make_catalog_db(database, [catalog_item("it-one")])
            index.write_text(
                json.dumps(dbr_record()) + "\n" + json.dumps(dbr_record(name_tag=None, name="Unmapped Sword")) + "\n",
                encoding="utf-8",
            )
            summary = build_report(index, database, output)
            results = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(summary["catalog_game_version"], "1.3.1.0")
        self.assertEqual(summary["catalog_category_records"], 2)
        self.assertEqual(summary["status_counts"], {"unmatched": 1, "unique": 1})
        self.assertEqual(len(results), 2)


if __name__ == "__main__":
    unittest.main()
