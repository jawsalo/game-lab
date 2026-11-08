from __future__ import annotations

import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from scripts.package_gd_edit import JAR_NAME, NOTICE_NAMES, install_archive


def _archive(entries: dict[str, bytes]) -> bytes:
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as bundle:
        for name, contents in entries.items():
            bundle.writestr(name, contents)
    return stream.getvalue()


class PackageGdEditTests(unittest.TestCase):
    def test_installs_jar_and_preserves_upstream_notices(self) -> None:
        entries = {
            JAR_NAME: b"jar-bytes",
            NOTICE_NAMES[0]: b"license text",
            NOTICE_NAMES[1]: b"third-party notices",
            "unneeded-launcher.sh": b"not installed",
        }
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "gd-edit"
            install_archive(_archive(entries), destination)

            self.assertEqual((destination / JAR_NAME).read_bytes(), b"jar-bytes")
            self.assertEqual(
                (destination / "licenses" / NOTICE_NAMES[0]).read_bytes(),
                b"license text",
            )
            self.assertEqual(
                (destination / "licenses" / NOTICE_NAMES[1]).read_bytes(),
                b"third-party notices",
            )
            self.assertFalse((destination / "unneeded-launcher.sh").exists())

    def test_rejects_archive_missing_upstream_notice(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(RuntimeError, "missing required files"):
                install_archive(
                    _archive({JAR_NAME: b"jar-bytes"}),
                    Path(temporary) / "gd-edit",
                )


if __name__ == "__main__":
    unittest.main()
