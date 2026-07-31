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

## Content Management API

The backend now includes a seeded movie catalog with genre management.

### Automatic sample data

On startup, the service runs `Base.metadata.create_all()` and seeds 20 sample movies with default genres if the `movies` table is empty. No extra seed command is required for a fresh local database.

To reseed locally, clear the catalog tables and restart the API:

```sql
DELETE FROM movie_genres;
DELETE FROM movies;
DELETE FROM genres;
```

### Movie endpoints

- `GET /movies`
- `GET /movies/{id}`
- `POST /movies` (requires bearer token)
- `PUT /movies/{id}` (requires bearer token)
- `DELETE /movies/{id}` (requires bearer token)
- `POST /movies/{id}/rating` (requires bearer token)
- `PUT /movies/{id}/rating` (requires bearer token)
- `DELETE /movies/{id}/rating` (requires bearer token)
- `GET /movies/{id}/reviews`
- `POST /movies/{id}/reviews` (requires bearer token)

`GET /movies` query parameters:

- `page`
- `page_size`
- `search`
- `sort_by=title|release_year`
- `sort_order=asc|desc`
- `genre`
- `language`

Movie responses now include:

- `average_rating`
- `total_ratings`
- `review_count`

### Genre endpoints

- `GET /genres`
- `POST /genres` (requires bearer token)
- `PUT /genres/{id}` (requires bearer token)
- `DELETE /genres/{id}` (requires bearer token)

### User experience endpoints

- `GET /watchlist` (requires bearer token)
- `POST /watchlist/{movie_id}` (requires bearer token)
- `DELETE /watchlist/{movie_id}` (requires bearer token)
- `GET /favorites` (requires bearer token)
- `POST /favorites/{movie_id}` (requires bearer token)
- `DELETE /favorites/{movie_id}` (requires bearer token)
- `GET /profile` (requires bearer token)
- `PUT /reviews/{review_id}` (requires bearer token, owner only)
- `DELETE /reviews/{review_id}` (requires bearer token, owner only)

### New database tables

- `watchlists`
- `favorites`
- `ratings`
- `reviews`

Each table uses foreign keys back to `users` and `movies`, plus uniqueness and supporting indexes where needed.

## Test

```bash
pytest
```

The full backend test suite covers:

- health and startup behavior
- movie and genre CRUD
- search and pagination
- watchlist CRUD
- favorites CRUD
- ratings
- reviews
- profile aggregation
- owner-only review permission checks

## Architecture

- `app/main.py` creates the FastAPI application and configures middleware.
- `app/api/` contains route registration and HTTP endpoints.
- `app/core/` contains application configuration and cross-cutting concerns.
- `app/db/` contains the SQLAlchemy declarative base, engine, session factory, and FastAPI database dependency.
- `app/models/` contains persistence models registered with the declarative base.
- `app/schemas/` contains request and response contracts.
- `app/services/` contains domain services such as catalog seeding.
- `app/utils/` contains shared utility functions.
- `tests/` contains automated API tests.
