## Backend (FastAPI)

FastAPI application providing APIs for the medical history system. Includes RBAC, auditing, and encryption in future phases.

### Run (local, via Docker - coming soon)
Will be orchestrated via root-level `docker-compose.yml`.

### Run (local, bare)
Create and activate a Python 3.11+ environment, install requirements, and run Uvicorn:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
