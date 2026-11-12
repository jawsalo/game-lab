"""Source-contract checks for source-backed control retaliation display."""

from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "apps" / "web" / "app.js"


class SpecialtyRetaliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_supported_effect_families(self):
        for source_type, display_type in (
            ("Fear", "Terrify"),
            ("Freeze", "Freeze"),
            ("Confusion", "Confuse"),
        ):
            with self.subTest(source_type=source_type):
                self.assertIn(f'["{source_type}", "{display_type}"]', self.source)
        self.assertIn('const chanceKey = `retaliation${sourceType}Chance`;', self.source)
        self.assertIn('const durationKey = `retaliation${sourceType}Min`;', self.source)

    def test_combined_display_preserves_rolls_and_other_fields(self):
        self.assertIn('label: `${displayType} Retaliation`', self.source)
        self.assertIn('displayValue: `${numberFormatter.format(probability)}% Chance of ${durationText} Seconds`', self.source)
        self.assertIn('chance.length !== 1 || duration.length !== 1', self.source)
        self.assertIn('result.filter((property) => property !== chance[0] && property !== seconds)', self.source)
        self.assertIn('combineSpecialtyRetaliation(general)', self.source)
        self.assertIn('key === "specialtyControlRetaliation") return "damage"', self.source)
        self.assertIn('property.key === "specialtyControlRetaliation"', self.source)
        self.assertIn('typeof property.displayValue === "string"', self.source)


if __name__ == "__main__":
    unittest.main()
