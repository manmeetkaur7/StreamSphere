# StreamSphere API

The StreamSphere backend is a modular FastAPI service for the StreamSphere platform. It currently provides the application foundation and a health endpoint; authentication and database integrations are intentionally not implemented yet.

## Requirements

- Python 3.11+
- pip

## Setup

From the `backend` directory, create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies and create local configuration:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
copy .env.example .env
```

Use `cp .env.example .env` instead of `copy` on macOS/Linux.

## Run the API

```bash
uvicorn app.main:app --reload
```

The API is available at [http://localhost:8000](http://localhost:8000).

- Health check: [http://localhost:8000/health](http://localhost:8000/health)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Test

```bash
pytest
```

## Architecture

- `app/main.py` creates the FastAPI application and configures middleware.
- `app/api/` contains route registration and HTTP endpoints.
- `app/core/` contains application configuration and cross-cutting concerns.
- `app/db/` is reserved for database configuration and sessions.
- `app/models/` is reserved for persistence models.
- `app/schemas/` contains request and response contracts.
- `app/services/` is reserved for domain and integration services.
- `app/utils/` contains shared utility functions.
- `tests/` contains automated API tests.

The service currently has no authentication, database, or external service dependencies.
