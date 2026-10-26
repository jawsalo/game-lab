"""Regression tests for the pinned Grim Dawn catalog."""

from __future__ import annotations

import unittest

from apps.api.app.catalog import GrimDawnCatalog


class GrimDawnCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = GrimDawnCatalog()

    def test_readiness_checks_catalog_identity_and_count(self) -> None:
        readiness = self.catalog.readiness()
        self.assertEqual(readiness["gameVersion"], "1.3.1.0")
        self.assertEqual(readiness["recordCount"], 8695)

    def test_metadata_matches_pinned_catalog(self) -> None:
        metadata = self.catalog.metadata()
        self.assertEqual(metadata["gameVersion"], "1.3.1.0")
        self.assertEqual(metadata["recordCount"], 8695)
        self.assertEqual(metadata["groups"]["equipment"], 6762)
        self.assertEqual(metadata["groups"]["component"], 107)

    def test_get_item_returns_stable_record(self) -> None:
        item = self.catalog.get_item("it11751")
        self.assertIsNotNone(item)
        assert item is not None
        self.assertEqual(item["name"], "Serenity")
        self.assertEqual(item["group"], "equipment")
        self.assertEqual(item["slot"], "Relic")

    def test_get_item_returns_none_for_unknown_id(self) -> None:
        self.assertIsNone(self.catalog.get_item("not-an-item"))

    def test_mythical_item_prefix_is_restored_from_raw_record(self) -> None:
        standard = self.catalog.get_item("it1027")
        mythical = self.catalog.get_item("it9040")
        self.assertIsNotNone(standard)
        self.assertIsNotNone(mythical)
        assert standard is not None
        assert mythical is not None

        self.assertEqual(standard["itemLevel"], 65)
        self.assertEqual(standard["name"], "Ring of the Black Matriarch")
        self.assertNotIn("itemStyleTag", standard["record"])

        self.assertEqual(mythical["itemLevel"], 94)
        self.assertEqual(
            mythical["record"]["itemStyleTag"],
            "tagStyleUniqueTier3",
        )
        self.assertEqual(
            mythical["name"],
            "Mythical Ring of the Black Matriarch",
        )

        highest = self.catalog.search_items(
            query="Black Matriarch",
            highest_level_only=True,
        )
        self.assertEqual(highest["total"], 1)
        self.assertEqual(highest["items"][0]["id"], "it9040")
        self.assertEqual(
            highest["items"][0]["name"],
            "Mythical Ring of the Black Matriarch",
        )

    def test_full_text_search_finds_component_and_recipe(self) -> None:
        result = self.catalog.search_items(query="Cracked Lodestone")
        self.assertEqual(result["total"], 2)
        self.assertEqual(
            {item["id"] for item in result["items"]},
            {"it2837", "it74"},
        )

    def test_exact_name_match_ranks_before_related_items(self) -> None:
        result = self.catalog.search_items(query="Serenity")
        self.assertGreater(result["total"], 1)
        self.assertEqual(result["items"][0]["id"], "it11751")
        self.assertEqual(result["items"][0]["name"], "Serenity")

    def test_filters_can_isolate_equipped_relics(self) -> None:
        result = self.catalog.search_items(
            item_group="equipment",
            category="ItemArtifact",
            slot="Relic",
            limit=100,
        )
        self.assertEqual(result["total"], 91)
        self.assertEqual(len(result["items"]), 91)
        self.assertTrue(
            all(item["slot"] == "Relic" for item in result["items"])
        )

    def test_pagination_is_bounded_and_stable(self) -> None:
        first = self.catalog.search_items(item_group="equipment", limit=2)
        second = self.catalog.search_items(
            item_group="equipment",
            limit=2,
            offset=2,
        )
        self.assertEqual(len(first["items"]), 2)
        self.assertEqual(len(second["items"]), 2)
        self.assertNotEqual(
            [item["id"] for item in first["items"]],
            [item["id"] for item in second["items"]],
        )


if __name__ == "__main__":
    unittest.main()
