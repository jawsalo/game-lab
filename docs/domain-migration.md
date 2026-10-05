# Domain migration

The routine migration path is intentionally short:

1. Lower the old DNS TTL ahead of the cutover.
2. Point the new domain's DNS records at the ingress address.
3. Change `platform.baseDomain` in the target environment file.
4. Run `make validate` and render the Helm chart.
5. Update truly external allowlists or OAuth callback registrations.
6. Deploy and verify the new certificate and routes.
7. Keep redirects from the old domain for a transition period when possible.

The old domain should not appear in application source, container images, or module defaults. CI enforces that the current deployment domain appears only in its approved environment file.
