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

# Validate the actual deployed HTML and assets, not just the API commit.
html="$(curl "${curl_options[@]}" "$base_url/")"
html_headers="$(curl "${curl_options[@]}" --head "$base_url/")"
js_url="$(printf '%s' "$html" | grep -oE '/app\\.js\\?v=[0-9a-f]{16}' | head -n 1)"
css_url="$(printf '%s' "$html" | grep -oE '/styles\\.css\\?v=[0-9a-f]{16}' | head -n 1)"
if [[ -z "$js_url" || -z "$css_url" ]] || ! grep -qi 'cache-control:.*no-cache' <<< "$html_headers"; then
  echo "Frontend smoke test failed: missing versioned assets or HTML revalidation header." >&2
  exit 1
fi
for asset_url in "$js_url" "$css_url"; do
  asset="$(curl "${curl_options[@]}" "$base_url$asset_url")"
  version="${asset_url##*v=}"
  actual="$(printf '%s' "$asset" | sha256sum | cut -c1-16)"
  if [[ "$actual" != "$version" ]]; then
    echo "Frontend smoke test failed: $asset_url content hash mismatch ($actual)." >&2
    exit 1
  fi
done

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
