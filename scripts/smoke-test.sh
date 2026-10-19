#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <base-url> <expected-version>" >&2
  exit 2
fi

base_url="${1%/}"
expected_version="$2"
curl_options=(
  --fail
  --silent
  --show-error
  --retry 10
  --retry-delay 2
  --retry-all-errors
)

if ! curl "${curl_options[@]}" "$base_url/" | grep --fixed-strings --quiet "<title>Game Lab</title>"; then
  echo "Web smoke test failed: Game Lab title not found." >&2
  exit 1
fi

metadata="$(curl "${curl_options[@]}" "$base_url/api")"
readiness="$(curl "${curl_options[@]}" "$base_url/api/health/ready")"
catalog="$(curl "${curl_options[@]}" "$base_url/api/grim-dawn/catalog")"
search="$(
  curl "${curl_options[@]}"     --get     --data-urlencode "q=Cracked Lodestone"     "$base_url/api/grim-dawn/items"
)"

python3 -c '
import json
import sys

expected_version, metadata_raw, readiness_raw, catalog_raw, search_raw = sys.argv[1:]
metadata = json.loads(metadata_raw)
readiness = json.loads(readiness_raw)
catalog = json.loads(catalog_raw)
search = json.loads(search_raw)

assert metadata["service"] == "game-lab-api", metadata
assert metadata["environment"] == "production", metadata
assert metadata["version"] == expected_version, metadata
assert readiness == {"status": "ready", "service": "game-lab-api"}, readiness
assert catalog["gameVersion"] == "1.3.1.0", catalog
assert catalog["recordCount"] == 8695, catalog
assert {item["id"] for item in search["items"]} == {"it2837", "it74"}, search
assert search["total"] == 2, search
' "$expected_version" "$metadata" "$readiness" "$catalog" "$search"

echo "Smoke tests passed for $base_url (API $expected_version, Grim Dawn 1.3.1.0 catalog)."
