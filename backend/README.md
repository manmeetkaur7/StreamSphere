# StreamSphere API

The StreamSphere backend is a modular FastAPI service for the StreamSphere platform. It provides the application foundation, health monitoring, SQLAlchemy 2.x PostgreSQL persistence, and JWT-based authentication.

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

Set `DATABASE_URL` in `.env` to the PostgreSQL instance used by your local environment. The example configuration points to `streamsphere` on the default PostgreSQL port.

Use `cp .env.example .env` instead of `copy` on macOS/Linux.

## Run the API

```bash
uvicorn app.main:app --reload
```

The API is available at [http://localhost:8000](http://localhost:8000).

- Health check: [http://localhost:8000/health](http://localhost:8000/health)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Authentication API

- `POST /auth/register` creates a user after validating the email, username, and password.
- `POST /auth/login` accepts OAuth2 password-form credentials and returns a bearer access token.

JWT signing configuration is provided through `JWT_SECRET_KEY`, `JWT_ALGORITHM`, and `ACCESS_TOKEN_EXPIRE_MINUTES`. Refresh tokens, email verification, and password reset are not implemented.

## Test

```bash
pytest
```

## Architecture

- `app/main.py` creates the FastAPI application and configures middleware.
- `app/api/` contains route registration and HTTP endpoints.
- `app/core/` contains application configuration and cross-cutting concerns.
- `app/db/` contains the SQLAlchemy declarative base, engine, session factory, and FastAPI database dependency.
- `app/models/` contains persistence models registered with the declarative base.
- `app/schemas/` contains request and response contracts.
- `app/services/` is reserved for domain and integration services.
- `app/utils/` contains shared utility functions.
- `tests/` contains automated API tests.

The service currently has no migrations, seed data, or external service integrations.
