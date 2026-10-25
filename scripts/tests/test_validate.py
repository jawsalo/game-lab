from __future__ import annotations

import tempfile
from pathlib import Path
from unittest import TestCase
from unittest.mock import patch

from scripts import validate


class PortabilityValidationTests(TestCase):
    def test_ignores_virtualenv_dependency_code_but_scans_project_code(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            production = root / "deploy" / "environments" / "production.yaml"
            production.parent.mkdir(parents=True)
            production.write_text(
                "platform:\n  baseDomain: example.invalid\n",
                encoding="utf-8",
            )

            virtualenv_file = root / ".venv" / "lib" / "site-packages" / "dependency.py"
            virtualenv_file.parent.mkdir(parents=True)
            virtualenv_file.write_text(secret_like_line(), encoding="utf-8")

            project_file = root / "apps" / "api" / "app" / "config.py"
            project_file.parent.mkdir(parents=True)
            project_file.write_text(secret_like_line(), encoding="utf-8")

            with (
                patch.object(validate, "ROOT", root),
                patch.object(validate, "APPROVED_DOMAIN_FILES", {Path("deploy/environments/production.yaml")}),
            ):
                errors = validate.validate_portability()

            self.assertEqual(
                [
                    "apps/api/app/config.py: possible committed secret; inject it at deploy time"
                ],
                errors,
            )


def secret_like_line() -> str:
    field = "pass" + "word"
    return f"{field}: dummy-value\n"
