"""Tests for the bounded read-only gd-edit subprocess wrapper."""

from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from apps.api.app.snapshot_parser import SnapshotParser, SnapshotParserError


class SnapshotParserTests(unittest.TestCase):
    def setUp(self) -> None:
        self.parser = SnapshotParser(
            java_executable="java-test",
            parser_jar="gd-edit-test.jar",
            worker_source_dir="worker-src",
            timeout_seconds=2,
            max_input_bytes=8,
            max_output_bytes=4096,
        )

    def test_character_parse_uses_temp_copy_and_returns_only_projection(self) -> None:
        output = {
            "character-name": "Synthetic Hero",
            "character-level": 100,
            "hardcore-mode": False,
            "equipment": [
                {
                    "basename": "records/items/example.dbr",
                    "stack-count": 1,
                    "private-field": "must not escape",
                }
            ],
            "inventory-sacks": [],
            "stashes": [],
            "meta-fileinfo": {
                "data-version": 8,
                "uuid": "private-uuid",
            },
            "meta-character-loaded-from": "/private/player.gdc",
        }
        observed: dict[str, object] = {}

        def fake_run(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
            observed["command"] = command
            observed["timeout"] = kwargs["timeout"]
            input_path = Path(command[-1])
            observed["input_exists_during_parse"] = input_path.is_file()
            observed["input_bytes"] = input_path.read_bytes()
            observed["input_path"] = str(input_path)
            return subprocess.CompletedProcess(command, 0, json.dumps(output), "")

        with patch("apps.api.app.snapshot_parser.subprocess.run", side_effect=fake_run):
            result = self.parser.parse_bytes("character", b"sample-gdc")

        self.assertEqual(result["sourceType"], "character")
        self.assertEqual(result["formatVersion"], 8)
        self.assertEqual(result["items"][0]["itemRecordPath"], "records/items/example.dbr")
        self.assertTrue(observed["input_exists_during_parse"])
        self.assertEqual(observed["input_bytes"], b"sample-gdc")
        self.assertFalse(Path(str(observed["input_path"])).exists())
        self.assertEqual(observed["timeout"], 2)
        command = observed["command"]
        assert isinstance(command, list)
        self.assertIn("-Xmx384m", command)
        self.assertIn("clojure.main", command)
        self.assertIn("game-lab.snapshot-worker", command)
        self.assertIn("private-uuid", json.dumps(result))
        self.assertNotIn("/private/player.gdc", json.dumps(result))
        self.assertNotIn("private-field", json.dumps(result))

    def test_shared_stash_parse_returns_tab_locations_without_tab_labels(self) -> None:
        output = {
            "version": 11,
            "stash": [
                {
                    "tab-name": "private label",
                    "inventory-items": [
                        {
                            "basename": "records/items/example.dbr",
                            "stack-count": 2,
                        }
                    ],
                }
            ],
            "meta-stash-loaded-from": "/private/transfer.gst",
        }
        with patch(
            "apps.api.app.snapshot_parser.subprocess.run",
            return_value=subprocess.CompletedProcess(
                ["java"], 0, json.dumps(output), ""
            ),
        ):
            result = self.parser.parse_bytes("sharedStash", b"gst")

        self.assertEqual(result["sourceType"], "sharedStash")
        self.assertEqual(result["formatVersion"], 11)
        self.assertEqual(
            result["items"][0]["location"],
            {"type": "sharedStash", "tabIndex": 0},
        )
        serialized = json.dumps(result)
        self.assertNotIn("private label", serialized)
        self.assertNotIn("/private/transfer.gst", serialized)

    def test_rejects_invalid_kind_empty_and_oversized_payloads_without_starting_java(
        self,
    ) -> None:
        with patch("apps.api.app.snapshot_parser.subprocess.run") as run:
            for source_type, payload in (
                ("unknown", b"x"),
                ("character", b""),
                ("character", b"123456789"),
            ):
                with self.subTest(source_type=source_type, payload=payload):
                    with self.assertRaises(SnapshotParserError):
                        self.parser.parse_bytes(source_type, payload)
            run.assert_not_called()

    def test_timeout_and_child_error_do_not_return_stderr(self) -> None:
        with patch(
            "apps.api.app.snapshot_parser.subprocess.run",
            side_effect=subprocess.TimeoutExpired("java", 2, stderr="private path"),
        ):
            with self.assertRaisesRegex(SnapshotParserError, "time limit") as raised:
                self.parser.parse_bytes("character", b"x")
            self.assertNotIn("private path", str(raised.exception))

        with patch(
            "apps.api.app.snapshot_parser.subprocess.run",
            return_value=subprocess.CompletedProcess(
                ["java"], 2, "", "private path and raw parser exception"
            ),
        ):
            with self.assertRaises(SnapshotParserError) as raised:
                self.parser.parse_bytes("character", b"x")
            self.assertNotIn("private path", str(raised.exception))
            self.assertNotIn("raw parser exception", str(raised.exception))


if __name__ == "__main__":
    unittest.main()
