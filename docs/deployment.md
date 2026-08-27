# Deployment Guide

StreamSphere is deployable as an independently hosted Next.js frontend plus a FastAPI service backed by managed PostgreSQL. Redis is optional: the API falls back to a process-local cache and rate-limit store when Redis is unavailable.

## Production configuration

Set these values in the backend environment:

| Variable | Required | Purpose |
| --- | --- | --- |
| `APP_ENV=production` | Yes | Enables production configuration validation. |
| `DATABASE_URL` | Yes | Managed PostgreSQL connection string. |
| `JWT_SECRET_KEY` | Yes | Long, unique secret for token signing. |
| `ALLOWED_ORIGINS` | Yes | Comma-separated, explicit frontend origins. |
| `REDIS_ENABLED` / `REDIS_URL` | Optional | Shared cache and rate-limit backend. |
| `AI_PROVIDER` | Yes | Use `mock` by default or `openai` when implemented. |
| `OPENAI_API_KEY` | Conditional | Required when `AI_PROVIDER=openai`. |
| `DEMO_MODE` | Optional | Seeds catalog data and disables destructive admin actions. |

Use the root [`.env.example`](../.env.example) as the complete local reference. Never commit a populated `.env` file.

## Frontend deployment

Deploy `frontend/` to Vercel or any Node.js host that supports `next build` and `next start`.

```text
NEXT_PUBLIC_API_BASE_URL=https://api.example.com
INTERNAL_API_BASE_URL=https://api.example.com
```

`NEXT_PUBLIC_API_BASE_URL` is compiled into browser code, so set it before the production build. `INTERNAL_API_BASE_URL` is used by server-rendered Next.js requests.

## Backend deployment

Deploy `backend/` to Render, Railway, Fly.io, AWS, or another Python container host. Use:

```text
Build: pip install -r requirements.txt
Start: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

Run migrations as a release command before switching traffic:

```bash
cd backend
alembic upgrade head
```

For an existing database created before Alembic, stamp the baseline once before upgrading:

```bash
alembic stamp 20260821_0001
alembic upgrade head
```

## Database and cache

Provision PostgreSQL 16-compatible managed storage and pass its private connection URL as `DATABASE_URL`. Provision Redis only when a shared cache/rate limit is desired. If Redis fails, `/health` reports `degraded` while requests continue with the in-memory fallback.

## CORS and health checks

Set `ALLOWED_ORIGINS` to exact deployed frontend origins, for example `https://app.example.com`. Do not use `*` in production. Configure the platform health check against `GET /health`; a missing database returns HTTP 503. `GET /metrics` supplies lightweight application counters for an authenticated network perimeter or internal monitoring setup.

## Rollback

Keep the previous backend image and frontend deployment available. Roll back application traffic first, then only downgrade an Alembic revision after verifying the migration supports it and data compatibility is understood. Database restores should use the managed provider's point-in-time recovery process.

## Troubleshooting

- A startup failure in production means one of the required values is unsafe or missing; inspect the error message without printing secrets.
- Browser `Failed to fetch` errors usually mean `NEXT_PUBLIC_API_BASE_URL`, `ALLOWED_ORIGINS`, or backend availability is incorrect.
- A `degraded` Redis result is expected when optional Redis is disabled or unreachable.
- Verify backend availability with `/health` and API contracts with `/docs`.
