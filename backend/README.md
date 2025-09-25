Medical History API (Backend)

FastAPI backend for a HIPAA-ready medical history recording application.

Quickstart
- Ensure Python 3.10+
- Install Poetry and dependencies
- Run the dev server

Commands
- cd backend
- poetry install
- poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Endpoints
- Docs: /api/v1/docs
- Health: /api/v1/health/ready

Environment
- Copy .env.example to .env and adjust as needed

Notes
- Logs are minimized to avoid PHI leakage
- Use a reverse proxy with TLS in production
