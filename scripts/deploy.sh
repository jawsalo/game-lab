#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: $0 <image-tag> <base-url>" >&2
  echo "Example: $0 sha-abcdef0 https://games.example.com" >&2
  exit 2
fi

image_tag="$1"
base_url="${2%/}"
release="${GAME_LAB_RELEASE:-game-lab}"
namespace="${GAME_LAB_NAMESPACE:-game-lab}"
values_file="${GAME_LAB_VALUES:-deploy/environments/production.yaml}"

if [[ ! "$image_tag" =~ ^sha-[0-9a-f]{7,40}$ ]]; then
  echo "Image tag must be an immutable Git SHA tag such as sha-abcdef0." >&2
  exit 2
fi

expected_version="${image_tag#sha-}"

python3 scripts/validate.py
helm lint deploy/chart --values "$values_file"

helm upgrade --install "$release" deploy/chart \
  --namespace "$namespace" \
  --values "$values_file" \
  --set-string modules.web.image.tag="$image_tag" \
  --set-string modules.api.image.tag="$image_tag" \
  --set-string modules.api.appVersion="$expected_version" \
  --rollback-on-failure \
  --wait \
  --timeout 5m

kubectl rollout status "deployment/${release}-web" --namespace "$namespace"
kubectl rollout status "deployment/${release}-api" --namespace "$namespace"

scripts/smoke-test.sh "$base_url" "$expected_version"
