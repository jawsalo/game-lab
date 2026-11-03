"""Synthetic tests for the gd-edit output allowlist."""

from __future__ import annotations

import json
import unittest

from apps.api.app.snapshot_projection import (
    SnapshotProjectionError,
    project_character,
    project_shared_stash,
)


class SnapshotProjectionTests(unittest.TestCase):
    def test_character_projection_keeps_item_instances_and_drops_parser_metadata(self) -> None:
        parsed = {
            "character-name": "Synthetic Hero",
            "character-level": 100,
            "hardcore-mode": False,
            "equipment": [
                {
                    "basename": "records/items/gearhead/example.dbr",
                    "prefix-name": "records/items/lootaffixes/prefix.dbr",
                    "stack-count": 1,
                    "seed": 73,
                    "attached": True,
                    "private-debug-field": "must not escape",
                },
                {"basename": ""},
            ],
            "inventory-sacks": [
                {
                    "inventory-items": [
                        {
                            "basename": "records/items/components/example.dbr",
                            "stack-count": 12,
                            "X": 2,
                            "Y": 4,
                            "augment-name": "records/items/augments/example.dbr",
                            "augment-seed": 9,
                        }
                    ]
                }
            ],
            "stashes": [
                {
                    "items": [
                        {
                            "basename": "records/items/gearrelic/example.dbr",
                            "stack-count": 1,
                            "X": 1.0,
                            "Y": 3.0,
                            "relic-name": "records/items/gearrelic/example.dbr",
                            "relic-completion-level": 4,
                        }
                    ],
                    "tab-name": "Private tab label",
                }
            ],
            "meta-fileinfo": {
                "data-version": 8,
                "uuid": "private-file-uuid",
                "seed": 9001,
            },
            "meta-character-loaded-from": "C:/private/path/player.gdc",
            "meta-block-list": [{"raw": "private parser internals"}],
        }

        projected = project_character(parsed)

        self.assertEqual(projected["sourceType"], "character")
        self.assertEqual(projected["formatVersion"], 8)
        self.assertEqual(
            projected["character"],
            {"name": "Synthetic Hero", "level": 100, "hardcore": False},
        )
        self.assertEqual(len(projected["items"]), 3)
        self.assertEqual(
            projected["items"][0],
            {
                "itemRecordPath": "records/items/gearhead/example.dbr",
                "location": {"type": "equipped", "slotIndex": 0},
                "prefixRecord": "records/items/lootaffixes/prefix.dbr",
                "stackCount": 1,
                "seed": 73,
            },
        )
        self.assertEqual(
            projected["items"][1]["location"],
            {"type": "carried", "sackIndex": 0},
        )
        self.assertEqual(projected["items"][1]["stackCount"], 12)
        self.assertEqual(
            projected["items"][2]["location"],
            {"type": "personalStash", "tabIndex": 0},
        )
        self.assertEqual(projected["items"][2]["relicCompletionLevel"], 4)

        serialized = json.dumps(projected)
        for secret in (
            "private-file-uuid",
            "private/path",
            "Private tab label",
            "private-debug-field",
            "meta-block-list",
        ):
            self.assertNotIn(secret, serialized)

    def test_shared_stash_projection_omits_tab_names_and_source_path(self) -> None:
        parsed = {
            "version": 11,
            "mod": "main",
            "expansion-status": 7,
            "stash": [
                {
                    "width": 10,
                    "height": 19,
                    "tab-name": "Private stash tab",
                    "inventory-items": [
                        {
                            "basename": "records/items/crafting/example.dbr",
                            "stack-count": 31,
                            "X": 1.0,
                            "Y": 17.0,
                        }
                    ],
                }
            ],
            "meta-stash-seed": 22,
            "meta-stash-loaded-from": "C:/private/path/transfer.gst",
        }

        projected = project_shared_stash(parsed)

        self.assertEqual(
            projected,
            {
                "sourceType": "sharedStash",
                "formatVersion": 11,
                "items": [
                    {
                        "itemRecordPath": "records/items/crafting/example.dbr",
                        "location": {"type": "sharedStash", "tabIndex": 0},
                        "stackCount": 31,
                        "x": 1.0,
                        "y": 17.0,
                    }
                ],
            },
        )
        serialized = json.dumps(projected)
        self.assertNotIn("Private stash tab", serialized)
        self.assertNotIn("private/path", serialized)
        self.assertNotIn("meta-stash-seed", serialized)

    def test_rejects_invalid_versions_and_malformed_items(self) -> None:
        with self.assertRaises(SnapshotProjectionError):
            project_shared_stash({"version": True, "stash": []})

        malformed = {
            "character-name": "Synthetic Hero",
            "character-level": 100,
            "hardcore-mode": False,
            "equipment": [{"basename": "records/items/example.dbr", "seed": "not-an-int"}],
            "inventory-sacks": [],
            "stashes": [],
            "meta-fileinfo": {"data-version": 8},
        }
        with self.assertRaises(SnapshotProjectionError):
            project_character(malformed)

    def test_rejects_non_finite_coordinates(self) -> None:
        malformed = {
            "version": 11,
            "stash": [
                {
                    "inventory-items": [
                        {
                            "basename": "records/items/example.dbr",
                            "X": float("nan"),
                        }
                    ]
                }
            ],
        }
        with self.assertRaises(SnapshotProjectionError):
            project_shared_stash(malformed)


if __name__ == "__main__":
    unittest.main()
