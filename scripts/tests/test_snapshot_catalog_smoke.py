"""Tests for local save-to-catalog smoke summaries."""

from __future__ import annotations

import unittest

from scripts.snapshot_catalog_smoke import resolve_path, summarize_items


class SnapshotCatalogSmokeTests(unittest.TestCase):
    def test_resolves_highest_priority_layer(self) -> None:
        rows = [
            {"source_layer": "base", "status": "unique", "candidates": [{"id": "it-base"}]},
            {"source_layer": "gdx3", "status": "unique", "candidates": [{"id": "it-gdx3"}]},
        ]
        self.assertEqual(resolve_path(rows, ("gdx3", "gdx2", "gdx1", "base")), ("unique", "gdx3"))

    def test_ambiguous_candidates_stay_ambiguous(self) -> None:
        rows = [{
            "source_layer": "base",
            "status": "ambiguous",
            "candidates": [{"id": "it-a"}, {"id": "it-b"}],
        }]
        self.assertEqual(resolve_path(rows, ("gdx3", "gdx2", "gdx1", "base")), ("ambiguous", "base"))

    def test_summarizes_instances_without_leaking_item_payloads(self) -> None:
        parsed = {
            "formatVersion": 8,
            "items": [
                {"itemRecordPath": "records/items/test.dbr", "name": "Private item name"},
                {"itemRecordPath": "records/items/test.dbr", "name": "Private item name"},
                {"itemRecordPath": "records/items/missing.dbr", "name": "Another item"},
            ],
        }
        report = {
            "records/items/test.dbr": [{
                "source_layer": "base",
                "status": "unique",
                "candidates": [{"id": "it-test"}],
            }]
        }

        result = summarize_items(parsed, report, ("gdx3", "gdx2", "gdx1", "base"))

        self.assertEqual(result["formatVersion"], 8)
        self.assertEqual(result["itemInstances"], 3)
        self.assertEqual(result["uniqueDBRPaths"], 2)
        self.assertEqual(result["countsByStatus"], {
            "unique": 2, "ambiguous": 0, "unmatched": 0, "missing": 1,
        })
        self.assertEqual(result["unresolvedPaths"][0]["path"], "records/items/missing.dbr")
        self.assertNotIn("Private item name", repr(result))


if __name__ == "__main__":
    unittest.main()
