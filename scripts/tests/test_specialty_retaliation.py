"""Source-contract checks for specialty fear retaliation display."""

from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "apps" / "web" / "app.js"


class FearRetaliationTests(unittest.TestCase):
    def test_fear_fields_are_combined_without_hiding_other_effects(self):
        source = SOURCE.read_text(encoding="utf-8")
        self.assertIn('property.key === "retaliationFearChance"', source)
        self.assertIn('property.key === "retaliationFearMin"', source)
        self.assertIn('key: "specialtyFearRetaliation"', source)
        self.assertIn('label: "Terrify Retaliation"', source)
        self.assertIn('displayValue: `${numberFormatter.format(probability)}% Chance of ${durationText} Seconds`', source)
        self.assertIn('combineSpecialtyRetaliation(general)', source)
        self.assertIn('return properties;', source)
        self.assertIn('key === "specialtyFearRetaliation") return "damage"', source)
        self.assertIn('typeof property.displayValue === "string"', source)


if __name__ == "__main__":
    unittest.main()
