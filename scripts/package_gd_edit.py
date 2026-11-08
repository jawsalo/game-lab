#!/usr/bin/env python3
"""Fetch and install the checksum-pinned gd-edit runtime for the API image."""

from __future__ import annotations

import argparse
import hashlib
import io
import urllib.request
import zipfile
from pathlib import Path


ARCHIVE_URL = (
    "https://github.com/GrimDawn-max/gd-edit/releases/download/"
    "v0.2.586/gd-edit-0.2.586-linux.zip"
)
ARCHIVE_SIZE = 21_666_582
ARCHIVE_SHA256 = "b6dde1d751971ef1a2e95e11ab6091bd94181c3a8db54effa6d2267fa8af8d9f"
JAR_NAME = "gd-edit-standalone.jar"
NOTICE_NAMES = ("LICENSE.txt", "THIRD-PARTY.txt")


def fetch_archive() -> bytes:
    request = urllib.request.Request(
        ARCHIVE_URL,
        headers={"User-Agent": "game-lab-build/1"},
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        archive = response.read(ARCHIVE_SIZE + 1)
    if len(archive) != ARCHIVE_SIZE:
        raise RuntimeError(f"Unexpected gd-edit archive size: {len(archive)}")
    digest = hashlib.sha256(archive).hexdigest()
    if digest != ARCHIVE_SHA256:
        raise RuntimeError(f"gd-edit archive checksum mismatch: {digest}")
    return archive


def install_archive(archive: bytes, destination: Path) -> None:
    """Install only the executable and required upstream license notices."""
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        members = set(bundle.namelist())
        required = {JAR_NAME, *NOTICE_NAMES}
        missing = required - members
        if missing:
            raise RuntimeError(f"gd-edit archive is missing required files: {sorted(missing)}")

        destination.mkdir(parents=True, exist_ok=False)
        jar_path = destination / JAR_NAME
        jar_path.write_bytes(bundle.read(JAR_NAME))
        jar_path.chmod(0o444)

        notices = destination / "licenses"
        notices.mkdir()
        for name in NOTICE_NAMES:
            notice_path = notices / name
            notice_path.write_bytes(bundle.read(name))
            notice_path.chmod(0o444)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", type=Path, required=True)
    args = parser.parse_args()
    install_archive(fetch_archive(), args.destination)


if __name__ == "__main__":
    main()
