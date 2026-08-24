# StreamSphere

StreamSphere is a full-stack streaming discovery platform with a Next.js frontend, a FastAPI backend, PostgreSQL persistence, Redis-backed caching with graceful fallback, real-time notifications, admin analytics, and AI-assisted discovery features.

## Stack

- Frontend: Next.js 16, React 19, TypeScript, Tailwind CSS 4
- Backend: FastAPI, SQLAlchemy 2, Pydantic, JWT auth
- Database: PostgreSQL
- Cache and transient infrastructure: Redis with in-memory fallback
- Migrations: Alembic
- Load testing: Locust
- DevOps: Docker Compose, GitHub Actions

## Production-Oriented Features

- Movie catalog, genres, filters, pagination, profiles, ratings, reviews, favorites, watchlists, and progress tracking
- AI search, AI summaries, recommendations, and personalized home feed
- Notifications with WebSocket delivery and REST fallback
- Admin moderation, admin stats, and platform analytics
- Redis-backed caching with safe in-memory fallback
- API rate limiting, structured request logging, request IDs, and lightweight `/metrics`
- Expanded `/health` endpoint with dependency state, uptime, version, and environment
- Security headers, structured safe error responses, and Argon2 password hashing for new passwords
- Alembic migration workflow with a baseline strategy for existing databases

## Architecture Docs

- System design: [docs/system-design.md](docs/system-design.md)
- Security notes: [docs/security.md](docs/security.md)
- Load testing: [load-tests/README.md](load-tests/README.md)

## Repository Layout

```text
streamsphere/
├── .github/workflows/ci.yml
├── backend/
│   ├── alembic/
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   ├── alembic.ini
│   ├── requirements.txt
│   └── .env.example
├── docs/
│   ├── security.md
│   └── system-design.md
├── frontend/
│   ├── app/
│   ├── components/
│   ├── lib/
│   ├── Dockerfile
│   └── package.json
├── load-tests/
│   ├── locustfile.py
│   └── README.md
├── docker-compose.yml
├── .env.example
└── README.md
```

## Environment Configuration

Copy the root example file:

```powershell
Copy-Item .env.example .env
```

Important variables:

- `DATABASE_URL`
- `REDIS_URL`
- `DB_POOL_SIZE`
- `DB_MAX_OVERFLOW`
- `JWT_SECRET_KEY`
- `ALLOWED_ORIGINS`
- `RATE_LIMIT_REQUESTS`
- `RATE_LIMIT_WINDOW_SECONDS`
- `AI_PROVIDER`
- `AI_REQUEST_TIMEOUT_SECONDS`
- `AI_REQUEST_RETRIES`
- `METRICS_ENABLED`
- `SECURITY_HEADERS_ENABLED`

The backend loads `.env` from the repository root and also supports `backend/.env` for backend-only local overrides.

## Local Startup

### Docker

```powershell
docker compose up --build
```

Services:

- Frontend: [http://localhost:3000](http://localhost:3000)
- Backend API: [http://localhost:8000](http://localhost:8000)
- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- Metrics: [http://localhost:8000/metrics](http://localhost:8000/metrics)

### Without Docker

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Frontend:

```powershell
cd frontend
npm ci
npm run dev
```

## Migrations

### Existing local database with data

Stamp the baseline first so Alembic does not try to recreate existing tables:

```powershell
cd backend
.\.venv\Scripts\alembic.exe stamp 20260821_0001
.\.venv\Scripts\alembic.exe upgrade head
```

### New empty database

```powershell
cd backend
.\.venv\Scripts\alembic.exe upgrade head
```

Downgrade one step:

```powershell
.\.venv\Scripts\alembic.exe downgrade -1
```

Current revisions:

- `20260821_0001` baseline schema
- `20260821_0002` Sprint 9 performance indexes

## Health, Metrics, and Security

`GET /health` returns:

- overall status
- environment
- version
- uptime
- PostgreSQL health
- Redis/cache backend health

`GET /metrics` returns safe internal counters such as:

- total requests
- average request latency
- request error counts
- cache hits and misses
- AI failure counts
- WebSocket connection counters

Security headers added in Sprint 9:

- `X-Content-Type-Options`
- `X-Frame-Options`
- `Referrer-Policy`
- `Content-Security-Policy`

## API Overview

Core public endpoints:

- `GET /health`
- `GET /metrics`
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

WebSocket endpoint:

- `/ws/notifications?token=<jwt>`

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

## Performance and Scalability Notes

- Compound indexes now support common read patterns for movies, notifications, analytics, ratings, favorites, watchlists, and progress.
- AI search avoids unnecessary N+1 genre loads.
- Admin review reads eagerly load related users to avoid repeated queries.
- Recommendation inputs invalidate consistently across ratings, reviews, favorites, watchlists, progress, and movie mutations.
- The modular monolith remains the right architecture now; future service boundaries are documented in [docs/system-design.md](docs/system-design.md).

## Load Testing and Benchmarking

Locust smoke configuration lives in [load-tests/locustfile.py](load-tests/locustfile.py).

Example local smoke run:

```powershell
backend\.venv\Scripts\locust.exe -f load-tests\locustfile.py --headless --users 5 --spawn-rate 1 --run-time 30s
```

This setup is intended for light local verification, not destructive stress tests.

## Testing and Validation

Backend:

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests -q --disable-warnings
```

Frontend:

```powershell
cd frontend
npm run lint
npm run build
```

Current verified status on Friday, August 21, 2026:

- `44` backend tests passing
- frontend lint passing
- frontend production build passing

## Continuous Integration

GitHub Actions workflow: `.github/workflows/ci.yml`

CI runs:

- backend dependency installation
- Alembic revision validation
- `alembic upgrade head`
- backend pytest
- frontend dependency installation
- frontend lint
- frontend production build
- `docker compose config`

## Notes

- Real `.env` files must never be committed.
- Redis fallback is expected to report `degraded` health when Redis is unavailable.
- Existing bcrypt password hashes remain verifiable for compatibility; new password hashes use Argon2.

## License

MIT
