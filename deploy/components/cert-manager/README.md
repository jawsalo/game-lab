# cert-manager

cert-manager is a cluster component, not a Game Lab chart dependency. Install and upgrade it independently, then create the ClusterIssuer named by `ingress.tls.clusterIssuer` in the environment values.

## Pinned version

The initial K3s deployment uses the cert-manager version recorded in `VERSION`. Install its complete static manifest from the matching upstream release:

```bash
CERT_MANAGER_VERSION="$(cat deploy/components/cert-manager/VERSION)"
sudo k3s kubectl apply -f "https://github.com/cert-manager/cert-manager/releases/download/${CERT_MANAGER_VERSION}/cert-manager.yaml"
sudo k3s kubectl wait --namespace cert-manager --for=condition=Available deployment --all --timeout=180s
sudo k3s kubectl get pods --namespace cert-manager
```

cert-manager must remain independently managed so replacing the application chart cannot accidentally remove cluster certificate infrastructure or its CRDs.

## ClusterIssuer

`cluster-issuer.example.yaml` is safe to publish and identifies Traefik by its standard ingress class. Create an ignored local copy and replace the placeholder ACME contact address before applying it:

```bash
cp deploy/components/cert-manager/cluster-issuer.example.yaml \
  deploy/components/cert-manager/cluster-issuer.local.yaml

sudo k3s kubectl apply \
  -f deploy/components/cert-manager/cluster-issuer.local.yaml

sudo k3s kubectl wait \
  --for=condition=Ready \
  clusterissuer/letsencrypt-prod \
  --timeout=120s
```

The local issuer file is excluded by the repository's `*.local.yaml` rule. Never commit a personal contact address, DNS-provider credential, or generated ACME account key.
