"""Tests for the highest-level catalog search option."""

from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from apps.api.app.catalog import GrimDawnCatalog


class HighestLevelCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_dir.name) / "items.sqlite"
        connection = sqlite3.connect(database_path)
        connection.execute(
            """
            CREATE TABLE items (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                name_sort TEXT NOT NULL,
                description TEXT,
                item_group TEXT NOT NULL,
                category TEXT NOT NULL,
                slot TEXT,
                rarity TEXT,
                level_requirement INTEGER,
                item_level INTEGER,
                bitmap TEXT,
                mods_json TEXT NOT NULL
            )
            """
        )
        connection.executemany(
            """
            INSERT INTO items (
                id, name, name_sort, description, item_group, category, slot,
                rarity, level_requirement, item_level, bitmap, mods_json
            ) VALUES (?, ?, ?, NULL, 'equipment', 'ArmorJewelry_Ring',
                      'Ring', 'Legendary', ?, ?, NULL, '[]')
            """,
            [
                ("ring_base", "Dreadguard", "dreadguard", 40, 40),
                (
                    "ring_empowered",
                    "Empowered Dreadguard",
                    "empowered dreadguard",
                    75,
                    75,
                ),
                (
                    "ring_mythical",
                    "Mythical Dreadguard",
                    "mythical dreadguard",
                    94,
                    94,
                ),
                ("ring_other", "Zealot's Ring", "zealot's ring", 50, 50),
            ],
        )
        connection.commit()
        connection.close()
        self.catalog = GrimDawnCatalog(database_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_keeps_highest_tier_and_paginates_after_deduplication(self) -> None:
        page = self.catalog.search_items(
            item_group="equipment",
            slot="Ring",
            highest_level_only=True,
            limit=1,
        )
        next_page = self.catalog.search_items(
            item_group="equipment",
            slot="Ring",
            highest_level_only=True,
            limit=1,
            offset=1,
        )

        self.assertEqual(page["total"], 2)
        self.assertEqual(page["items"][0]["name"], "Mythical Dreadguard")
        self.assertEqual(next_page["total"], 2)
        self.assertEqual(next_page["items"][0]["name"], "Zealot's Ring")

    def test_preserves_legacy_results_when_option_is_off(self) -> None:
        result = self.catalog.search_items(
            item_group="equipment",
            slot="Ring",
            limit=100,
        )
        self.assertEqual(result["total"], 4)


if __name__ == "__main__":
    unittest.main()
