#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repo_root"

if ! command -v kubectl >/dev/null || ! command -v helm >/dev/null; then
  echo "kubectl and Helm are required." >&2
  exit 2
fi

echo "Kubernetes context: $(kubectl config current-context)"
echo "Nodes:"
kubectl get nodes -o wide
echo
echo "Current node usage (requires metrics-server):"
kubectl top nodes || {
  echo "kubectl top nodes failed; verify metrics-server and node capacity before deploying." >&2
  exit 2
}
echo
echo "Host disk:"
df -h /
disk_available_bytes="$(df --output=avail -B1 / | tail -n 1 | tr -d ' ')"
minimum_disk_bytes=$((30 * 1024 * 1024 * 1024))
if (( disk_available_bytes < minimum_disk_bytes )); then
  echo "At least 30 GiB free host disk is required; stopping before cluster changes." >&2
  exit 2
fi
echo
echo "Planned persistent claims total 22Gi (Prometheus 8Gi, Loki 8Gi, Tempo 5Gi, Grafana 1Gi)."
echo "Confirm at least 4 GiB of node memory remains available."
read -r -p "After checking capacity, type deploy to continue: " answer
if [[ "$answer" != "deploy" ]]; then
  echo "Stopped before making cluster changes."
  exit 1
fi

if [[ -z "${GRAFANA_ADMIN_PASSWORD:-}" ]]; then
  read -r -s -p "Choose a Grafana admin password: " GRAFANA_ADMIN_PASSWORD
  echo
fi
if [[ -z "${GRAFANA_ADMIN_PASSWORD:-}" ]]; then
  echo "Grafana admin password cannot be empty." >&2
  exit 2
fi

helm repo add prometheus-community https://prometheus-community.github.io/helm-charts --force-update
helm repo add grafana-community https://grafana-community.github.io/helm-charts --force-update
helm repo add grafana https://grafana.github.io/helm-charts --force-update
helm repo update

# Render every pinned chart before creating namespace resources or secrets.
helm template prometheus prometheus-community/prometheus \
  --namespace observability --version 29.37.0 \
  --values observability/values/prometheus.yaml >/dev/null
helm template grafana grafana-community/grafana \
  --namespace observability --version 14.0.1 \
  --values observability/values/grafana.yaml >/dev/null
helm template loki grafana-community/loki \
  --namespace observability --version 19.0.0 \
  --values observability/values/loki.yaml >/dev/null
helm template tempo grafana-community/tempo \
  --namespace observability --version 3.2.0 \
  --values observability/values/tempo.yaml >/dev/null
helm template alloy grafana/alloy \
  --namespace observability --version 1.14.0 \
  --values observability/values/alloy.yaml \
  --set-file alloy.configMap.content=observability/alloy.alloy >/dev/null

kubectl create namespace observability --dry-run=client -o yaml | kubectl apply -f -
kubectl -n observability create secret generic grafana-admin \
  --from-literal=admin-user=admin \
  --from-literal=admin-password="$GRAFANA_ADMIN_PASSWORD" \
  --dry-run=client -o yaml | kubectl apply -f -
unset GRAFANA_ADMIN_PASSWORD

helm upgrade --install prometheus prometheus-community/prometheus \
  --namespace observability --version 29.37.0 \
  --values observability/values/prometheus.yaml --wait --timeout 10m

helm upgrade --install grafana grafana-community/grafana \
  --namespace observability --version 14.0.1 \
  --values observability/values/grafana.yaml --wait --timeout 10m

helm upgrade --install loki grafana-community/loki \
  --namespace observability --version 19.0.0 \
  --values observability/values/loki.yaml --wait --timeout 15m

helm upgrade --install tempo grafana-community/tempo \
  --namespace observability --version 3.2.0 \
  --values observability/values/tempo.yaml --wait --timeout 10m

helm upgrade --install alloy grafana/alloy \
  --namespace observability --version 1.14.0 \
  --values observability/values/alloy.yaml \
  --set-file alloy.configMap.content=observability/alloy.alloy \
  --wait --timeout 10m

kubectl -n observability get deployments,statefulsets,pods,pvc
echo
echo "Grafana remains private. Use: kubectl -n observability port-forward svc/grafana 3000:80"
