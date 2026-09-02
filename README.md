# StreamSphere

StreamSphere is a full-stack movie discovery platform built with Next.js, FastAPI, and PostgreSQL. It combines movie discovery, personalized recommendations, watchlists, ratings, reviews, and legal demo playback in one application.

AI-assisted search and recommendations help users find movies based on their interests and activity.

## Live Demo

Frontend: [https://stream-sphere-beta.vercel.app](https://stream-sphere-beta.vercel.app)

## Features

- Movie catalog with search, genre and language filters, sorting, and pagination
- JWT authentication and user profiles
- Personal watchlists and favorites
- Movie ratings and reviews
- AI-assisted search, summaries, and recommendations
- Real-time notifications with a REST fallback
- Admin moderation and analytics tools
- Legal demo playback using direct HTML5 video sources

## Tech Stack

**Frontend:** Next.js, TypeScript, React, Tailwind CSS

**Backend:** FastAPI, Python, SQLAlchemy, Pydantic, JWT authentication

**Data and infrastructure:** PostgreSQL, Redis, Alembic, Docker Compose, GitHub Actions, Locust, Render, and Vercel

## Architecture

The Next.js frontend provides the catalog and authenticated user experience. FastAPI exposes REST and WebSocket APIs, and SQLAlchemy stores application data in PostgreSQL. Redis supports caching and rate limiting when available, with an in-memory fallback for local development.

See [the architecture summary](docs/architecture-summary.md) and [the system design](docs/system-design.md) for component boundaries and technical tradeoffs.

## Configuration

Copy `.env.example` to `.env` for Docker Compose, or `backend/.env.example` to `backend/.env` for a backend-only setup. Keep populated environment files out of version control.

For production, configure `DATABASE_URL`, a non-default `JWT_SECRET_KEY`, and explicit `ALLOWED_ORIGINS`.

## Local Setup

### Docker

```powershell
Copy-Item .env.example .env
docker compose up --build
```

- Frontend: http://localhost:3000
- API: http://localhost:8000
- API docs: http://localhost:8000/docs

### Without Docker

Start PostgreSQL and configure `DATABASE_URL` in a local `.env` file. Then run the backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

In another terminal, start the frontend:

```powershell
cd frontend
npm ci
npm run dev
```

For an existing database created before Alembic, review [the deployment guide](docs/deployment.md) before running migrations.

## Testing

Run backend tests from the repository root:

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests
```

Run frontend checks from the `frontend` directory:

```powershell
npm run lint
npm run build
```

Optional Locust smoke tests are documented in [load-tests/README.md](load-tests/README.md).

## Deployment

Deploy the frontend to Vercel and the backend to Render with PostgreSQL. Redis is optional but recommended when running multiple API instances.

See [the deployment guide](docs/deployment.md) for environment configuration and migration details.

## Project Structure

```text
streamsphere/
|-- .github/workflows/ci.yml
|-- backend/
|   |-- alembic/
|   |-- app/
|   `-- tests/
|-- docs/
|   |-- architecture-summary.md
|   |-- demo-playback.md
|   |-- deployment.md
|   `-- system-design.md
|-- frontend/
|   |-- app/
|   |-- components/
|   `-- lib/
|-- load-tests/
|-- docker-compose.yml
`-- .env.example
```

## Demo Media Attribution

The seeded catalog titles are fictional. Playback uses legal, openly licensed demo footage through the native HTML5 player and is not represented as original movie footage or trailers. See [demo media attribution](docs/demo-playback.md).

## License

MIT
