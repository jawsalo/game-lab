# Architecture

Game Lab separates portable application behavior from environment-owned deployment details.

## Configuration contract

`deploy/environments/<environment>.yaml` is the authoritative integration point. It owns the base domain, optional hostname overrides, enabled modules, ingress class, and certificate issuer name.

The chart derives each default public hostname as:

```text
<module.subdomain>.<platform.baseDomain>
```

A module can instead provide a complete `hostname`. Application code must not repeat either value.

## Boundaries

- Public traffic enters through a standard Kubernetes `Ingress`.
- Internal calls use Kubernetes service names, not public DNS.
- The web client should use same-origin `/api` routes when the API is added.
- Modules can be enabled or replaced without changing unrelated modules.
- cert-manager and observability are lifecycle-independent platform components.
- Secret values are deployment inputs and never chart defaults.

This keeps a future domain migration constrained to DNS, environment values, certificate reconciliation, and genuinely external callback registrations.
