## Medical History Recording Application

This repository contains a secure, HIPAA-aligned medical history recording application.

### Monorepo Layout
- `apps/backend`: FastAPI-based backend (API, DB models, migrations)
- `infra`: Infrastructure-as-code, local `docker-compose` for dev services

### Quick Start (coming soon)
Infrastructure and services will be provisioned with `docker-compose`. See `infra/README.md` for details once available.

### Development Environment
- Copy `.env.example` to `.env` and update values
- Use Python 3.11+

### Compliance
This project aims to support HIPAA best practices through encryption, access controls, auditing, and secure defaults. Final compliance depends on deployment, organizational controls, and operational processes.
