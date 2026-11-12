"""Regression contract for source-backed poison retaliation duration."""

from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "apps" / "web" / "app.js"


class PoisonRetaliationDurationTests(unittest.TestCase):
    def test_duration_is_attached_only_to_matching_poison_retaliation(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn('property.key === "retaliationSlowPoisonMin"', source)
        self.assertIn('property.key === "retaliationSlowPoisonDurationMin"', source)
        self.assertIn('poison.length !== 1 || duration.length !== 1', source)
        self.assertIn('duration[0].value <= 0', source)
        self.assertIn('Poison Retaliation over ${numberFormatter.format(duration[0].value)} Seconds', source)
        self.assertIn('property !== duration[0]', source)
        self.assertIn('combinePoisonRetaliationDuration(combineSpecialtyRetaliation(general))', source)
        self.assertIn('if (property.key === "retaliationSlowPoisonMin" && property.label) return property.label;', source)


if __name__ == "__main__":
    unittest.main()
