## Infrastructure

This directory contains local development infrastructure definitions (e.g., `docker-compose`).

Services (planned):
- Postgres (application database)
- Keycloak (identity provider for OAuth2/OIDC)

Production infrastructure should be provisioned via a secure IaC toolchain (Terraform/Pulumi) with hardened configurations and secrets management (e.g., Vault, AWS Secrets Manager).
