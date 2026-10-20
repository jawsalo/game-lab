"""Tests for the display-safe Grim Dawn item card contract."""

from __future__ import annotations

import unittest

from apps.api.app.item_card import build_item_card


class ItemCardTests(unittest.TestCase):
    def test_description_tokens_become_semantic_segments(self) -> None:
        card = build_item_card(
            {
                "id": "it14519",
                "name": "Aeon's Eye",
                "group": "equipment",
                "category": "ArmorJewelry_Amulet",
                "description": "Flavor ^oorange^w white^n normal",
                "record": {},
            }
        )

        self.assertEqual(
            [segment.dict() for segment in card.description or []],
            [
                {"text": "Flavor ", "style": "default"},
                {"text": "orange", "style": "accent"},
                {"text": " white", "style": "white"},
                {"text": " normal", "style": "default"},
            ],
        )

    def test_missing_description_is_omitted_from_card(self) -> None:
        card = build_item_card(
            {
                "id": "it10",
                "name": "Blueprint: Myrmidon Visor",
                "group": "recipe",
                "category": "ItemArtifactFormula",
                "description": None,
                "record": {},
            }
        )

        self.assertIsNone(card.description)
        self.assertNotIn("description", card.dict(by_alias=True, exclude_none=True))

    def test_properties_conversions_and_expansions_are_separate(self) -> None:
        card = build_item_card(
            {
                "id": "it11751",
                "name": "Serenity",
                "group": "equipment",
                "category": "ItemArtifact",
                "slot": "Relic",
                "rarity": "Legendary",
                "levelRequirement": 90,
                "itemLevel": 90,
                "mods": ["gdx2"],
                "record": {
                    "characterLife": 300,
                    "defensiveAether": 25,
                    "conversionInType": "physical",
                    "conversionOutType": "vitality",
                    "conversionPercentage": 100,
                    "itemLevel": 90,
                    "maxAffixes": 0,
                },
            }
        )
        payload = card.dict(by_alias=True, exclude_none=True)

        self.assertEqual(payload["expansions"], ["gdx2"])
        self.assertEqual(
            payload["properties"],
            [
                {"key": "characterLife", "value": 300},
                {"key": "defensiveAether", "value": 25},
            ],
        )
        self.assertEqual(
            payload["conversions"],
            [{"from": "physical", "to": "vitality", "percentage": 100}],
        )
        self.assertNotIn("record", payload)
        self.assertNotIn("mods", payload)

    def test_recipe_includes_output_cost_and_alternative_ingredients(self) -> None:
        card = build_item_card(
            {
                "id": "it10",
                "name": "Blueprint: Myrmidon Visor",
                "group": "recipe",
                "category": "ItemArtifactFormula",
                "description": None,
                "record": {
                    "artifactName": "it1348",
                    "artifactCreateQuantity": 1,
                    "artifactCreationCost": 60000,
                    "reagent1BaseName": "it2900",
                    "reagent1Quantity": 1,
                    "reagentBaseBaseName": ["it1306", "it1307"],
                    "reagentBaseQuantity": 1,
                },
            }
        )
        recipe = card.dict(by_alias=True)["recipe"]

        self.assertEqual(recipe["outputItemId"], "it1348")
        self.assertEqual(recipe["outputQuantity"], 1)
        self.assertEqual(recipe["craftingCost"], 60000)
        self.assertEqual(
            recipe["ingredients"],
            [
                {"itemIds": ["it1306", "it1307"], "quantity": 1},
                {"itemIds": ["it2900"], "quantity": 1},
            ],
        )


if __name__ == "__main__":
    unittest.main()
