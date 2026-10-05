# Operations baseline

The initial target is a single-node K3s server using the built-in Traefik ingress controller.

## Deployment prerequisites

- DNS A/AAAA records point to the intended public address.
- TCP ports 80 and 443 are allowed only when public ingress is ready.
- cert-manager is installed once at the cluster level.
- A matching ClusterIssuer exists before production TLS is requested.
- A local values file or secret manager supplies every secret.

## Safe release sequence

```bash
make validate
make helm-lint ENV=production
make helm-render ENV=production
helm upgrade --install game-lab deploy/chart \
  --namespace game-lab \
  --create-namespace \
  -f deploy/environments/production.yaml
```

Before a first production release, inspect the rendered manifests and replace image tags with immutable digests as application images are introduced.
