#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <base-url> <expected-version>" >&2
  exit 2
fi

base_url="${1%/}"
expected_version="$2"

if ! curl --fail --silent --show-error "$base_url/" | grep --fixed-strings --quiet "<title>Game Lab</title>"; then
  echo "Web smoke test failed: Game Lab title not found." >&2
  exit 1
fi

metadata="$(curl --fail --silent --show-error "$base_url/api")"
readiness="$(curl --fail --silent --show-error "$base_url/api/health/ready")"

python3 -c '
import json
import sys

expected_version, metadata_raw, readiness_raw = sys.argv[1:]
metadata = json.loads(metadata_raw)
readiness = json.loads(readiness_raw)

assert metadata["service"] == "game-lab-api", metadata
assert metadata["environment"] == "production", metadata
assert metadata["version"] == expected_version, metadata
assert readiness == {"status": "ready", "service": "game-lab-api"}, readiness
' "$expected_version" "$metadata" "$readiness"

echo "Smoke tests passed for $base_url (API $expected_version)."
