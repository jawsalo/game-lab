"""Regression checks for frontend crowd-control resistance labels (backlog #22)."""

from pathlib import Path
import re
import unittest


APP_JS = Path(__file__).resolve().parents[2] / "apps" / "web" / "app.js"


class ResistanceLabelContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = APP_JS.read_text(encoding="utf-8")
        cls.labels = cls.source.split("const PROPERTY_LABELS = {", 1)[1].split("\n};", 1)[0]
        cls.classifier = cls.source.split("function classifyItemProperty(key) {", 1)[1].split("\n}", 1)[0]

    def test_player_facing_resistance_labels(self):
        expected = {
            "defensiveTrap": "Entrapment Resistance",
            "defensiveStun": "Stun Resistance",
            "defensiveSlowLifeLeach": "Life Leech Resistance",
            "defensiveSlowLifeLeech": "Life Leech Resistance",
            "defensiveTotalSpeed": "Slow Resistance",
            "defensiveFreeze": "Freeze Resistance",
            "defensivePetrify": "Petrify Resistance",
            "defensiveSleep": "Sleep Resistance",
            "defensiveConfusion": "Confusion Resistance",
            "defensiveFear": "Fear Resistance",
        }
        for key, label in expected.items():
            with self.subTest(key=key):
                self.assertIn(f'{key}: "{label}"', self.labels)

    def test_resistance_keys_group_under_defense(self):
        match = re.search(r"/\^defensive\(\?:([^)]*)\)\$/.test\(key\)", self.classifier)
        self.assertIsNotNone(match, "Explicit defensive crowd-control family missing")
        variants = set(match.group(1).split("|"))
        self.assertTrue({
            "Trap", "Stun", "SlowLifeLeach", "SlowLifeLeech",
            "TotalSpeed", "Freeze", "Petrify", "Sleep", "Confusion", "Fear",
        }.issubset(variants))
        self.assertIn('return "defense";', self.classifier)

    def test_no_broad_offensive_or_retaliation_rewrite(self):
        self.assertNotIn('offensiveSlowLifeLeach:', self.labels)
        self.assertNotIn('retaliationSlowLifeLeach:', self.labels)


if __name__ == "__main__":
    unittest.main()
