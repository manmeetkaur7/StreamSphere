# StreamSphere

StreamSphere is a full-stack streaming discovery platform with a Next.js frontend, a FastAPI backend, PostgreSQL persistence, Redis-backed caching with graceful fallback, AI-assisted discovery features, real-time notifications, admin analytics, and Docker-based local orchestration.

## Stack

- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS 4
- Backend: FastAPI, SQLAlchemy 2, Pydantic, JWT auth
- Database: PostgreSQL
- Cache and transient infrastructure: Redis with in-memory fallback
- DevOps: Docker Compose, GitHub Actions

## Production Features

- Redis-backed caching for recommendations, AI search, and movie summaries
- Graceful fallback to in-memory cache when Redis is disabled or unavailable
- API rate limiting middleware with configurable thresholds
- Structured JSON request logging with request IDs
- Expanded `/health` endpoint with database, Redis, uptime, version, and environment details
- OpenAPI metadata with tagged sections and operational descriptions
- Real-time notifications with WebSocket delivery and frontend REST fallback
- Admin moderation, stats, and platform analytics APIs
- Personal profile insights backed by SQL activity aggregates
- Background job abstraction built on FastAPI `BackgroundTasks`
- Dockerfiles for backend and frontend plus a complete `docker-compose.yml`
- CI workflow for backend tests, frontend lint/build, and Compose validation

## Repository Layout

```text
streamsphere/
├── .github/workflows/ci.yml
├── backend/
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml
├── .env.example
└── README.md
```

## Environment Configuration

1. Copy the root example file:

```bash
cp .env.example .env
```

PowerShell:

```powershell
Copy-Item .env.example .env
```

2. Review or change the important values:

- `DATABASE_URL`
- `REDIS_URL`
- `JWT_SECRET_KEY`
- `ALLOWED_ORIGINS`
- `NEXT_PUBLIC_API_BASE_URL`
- `INTERNAL_API_BASE_URL`
- `RATE_LIMIT_REQUESTS`
- `RATE_LIMIT_WINDOW_SECONDS`
- `AI_PROVIDER`

The backend loads `.env` from the repository root and also supports `backend/.env` for backend-only local overrides.

For local browser work, include both `http://localhost:3000` and `http://127.0.0.1:3000` in `ALLOWED_ORIGINS`.

## Run Locally With Docker

This is the primary local startup path.

```bash
docker compose up --build
```

Services:

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8000](http://localhost:8000)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

Stop the stack:

```bash
docker compose down
```

Remove the Postgres volume too:

```bash
docker compose down -v
```

## Run Without Docker

### Backend

```bash
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm ci
npm run dev
```

## Health and Operations

`GET /health` returns:

- overall status
- environment
- running version
- uptime in seconds
- PostgreSQL status
- Redis status and active backend

Status behavior:

- `ok`: required dependencies are healthy and Redis is active
- `degraded`: the app is serving traffic with a fallback, such as in-memory cache
- `unavailable`: a required dependency such as the database is unavailable

## Sprint 8 Architecture

### Notifications

- `notifications` stores user-scoped notification events, read state, and timestamps.
- REST endpoints provide list, unread count, mark-as-read, mark-all-read, and delete operations.
- WebSocket clients connect to `/ws/notifications` with the existing JWT access token.
- The backend maintains a per-user connection manager so multiple sessions for the same account receive the same events.
- The frontend bell uses WebSockets when available and falls back to REST refresh if the socket disconnects.

### Admin Authorization

- `users.is_admin` gates admin-only routes through `require_admin`.
- Authenticated non-admin users receive `403 Forbidden` on admin routes.
- `users.is_active` blocks inactive users from logging in or authenticating protected endpoints.

Promote a local admin safely:

```sql
UPDATE users
SET is_admin = TRUE
WHERE email = 'your-local-user@example.com';
```

Do not hardcode an admin password or admin email in application code.

### Analytics

- `activity_events` tracks `login`, `movie_view`, `ai_search`, `rating`, `review`, `favorite`, `watchlist_add`, `progress_update`, and `recommendation_generated`.
- Event metadata is sanitized before persistence so keys like `password`, `token`, `jwt`, `authorization`, `api_key`, and `secret` are removed.
- Profile insights and admin analytics use SQL aggregates instead of loading full tables into Python.

### Background Jobs

- `BackgroundJobDispatcher` queues notification generation, recommendation refreshes, and AI summary regeneration through FastAPI `BackgroundTasks`.
- Routes depend on the abstraction so a real queue such as Celery or RQ can replace it later without route rewrites.

## Caching

Redis caching is enabled with `REDIS_ENABLED=true`.

Cached flows:

- recommendations
- AI search responses
- movie summaries

Fallback behavior:

- If Redis is reachable, StreamSphere uses Redis.
- If Redis is disabled or unavailable, the backend falls back to in-memory storage.
- Health reporting reflects that fallback with a `degraded` Redis status.

Relevant env vars:

- `REDIS_ENABLED`
- `REDIS_URL`
- `CACHE_DEFAULT_TTL_SECONDS`
- `RECOMMENDATION_CACHE_TTL_SECONDS`
- `AI_SEARCH_CACHE_TTL_SECONDS`
- `MOVIE_SUMMARY_CACHE_TTL_SECONDS`

## Rate Limiting

Rate limiting is applied at the API middleware layer.

Defaults:

- `RATE_LIMIT_REQUESTS=120`
- `RATE_LIMIT_WINDOW_SECONDS=60`

Exempt paths default to:

- `/health`
- `/docs`
- `/redoc`
- `/openapi.json`

Responses include:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `Retry-After` when the limit is exceeded

## Structured Logging

Each request emits a structured JSON log record with:

- `event`
- `request_id`
- `method`
- `path`
- `status_code`
- `duration_ms`
- `client_ip`

Each response also includes `X-Request-ID`.

## OpenAPI Documentation

Swagger UI and ReDoc are enabled by default and grouped with tagged sections such as:

- `health`
- `authentication`
- `movies`
- `genres`
- `notifications`
- `watchlist`
- `favorites`
- `reviews`
- `recommendations`
- `search`
- `home`
- `profile`
- `admin`

You can disable docs in restricted environments with:

```env
DOCS_ENABLED=false
```

## API Overview

Core public endpoints:

- `GET /health`
- `GET /movies`
- `GET /movies/trending`
- `GET /movies/{id}`
- `GET /movies/{id}/summary`
- `GET /movies/{id}/reviews`
- `GET /genres`
- `POST /search/ai`

Authenticated endpoints:

- `POST /auth/register`
- `POST /auth/login`
- `GET /notifications`
- `GET /notifications/unread-count`
- `PUT /notifications/{id}/read`
- `PUT /notifications/read-all`
- `DELETE /notifications/{id}`
- `GET /watchlist`
- `POST /watchlist/{movie_id}`
- `DELETE /watchlist/{movie_id}`
- `GET /favorites`
- `POST /favorites/{movie_id}`
- `DELETE /favorites/{movie_id}`
- `GET /continue-watching`
- `POST /movies/{id}/progress`
- `PUT /movies/{id}/progress`
- `GET /recommendations`
- `GET /home`
- `GET /profile`
- `GET /profile/insights`
- movie CRUD, rating, and review maintenance endpoints

Real-time endpoint:

- WebSocket `/ws/notifications?token=<jwt>`

Admin endpoints:

- `GET /admin/stats`
- `GET /admin/users`
- `GET /admin/movies`
- `GET /admin/reviews`
- `PUT /admin/users/{id}/status`
- `DELETE /admin/reviews/{id}`
- `GET /admin/analytics`
- `POST /movies/{id}/summary/regenerate`
- `POST /admin/recommendations/recompute`
- `DELETE /admin/recommendations/cache`

Frontend pages:

- `/`
- `/movies`
- `/movies/[id]`
- `/profile`
- `/admin` for admins only

## Testing and Validation

Backend:

```bash
cd backend
.\.venv\Scripts\python.exe -m pytest
```

Frontend lint:

```bash
cd frontend
npm run lint
```

Frontend build:

```bash
cd frontend
npm run build
```

Current backend status:

- `37` passing backend tests

The backend suite covers:

- health and startup behavior
- movie and genre CRUD
- search and pagination
- watchlists and favorites
- ratings and reviews
- profiles and AI features
- cache fallback behavior
- rate limiting
- structured logging
- OpenAPI metadata
- notifications and ownership checks
- WebSocket authentication and delivery
- admin permissions, moderation, stats, and analytics
- personal insights and activity tracking

## Continuous Integration

GitHub Actions workflow: `.github/workflows/ci.yml`

It runs:

- backend pytest against PostgreSQL and Redis service containers
- frontend lint
- frontend production build
- `docker compose config` validation

## Notes About Existing Warnings

The frontend lint step currently reports existing `next/image` warnings for legacy `<img>` usage in a few components. They are warnings, not errors, and do not block the build or test suite.

## License

MIT
