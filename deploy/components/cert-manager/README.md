# cert-manager

cert-manager is a cluster component, not a Game Lab chart dependency. Install and upgrade it independently, then create the ClusterIssuer named by `ingress.tls.clusterIssuer` in the environment values.

The issuer manifest contains account-specific email and possibly secret references, so keep the real manifest outside this public repository. A sanitized example can be added when the cluster bootstrap workflow is implemented.
