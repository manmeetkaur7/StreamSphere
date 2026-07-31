# StreamSphere

StreamSphere is a full-stack streaming discovery platform designed to bring content browsing, personalized organization, and provider availability into one focused experience. The repository is organized as a production-oriented monorepo with a Next.js frontend, a FastAPI service layer, PostgreSQL persistence, and Docker-based local infrastructure.

## Architecture

StreamSphere follows a layered client-service-data architecture:

```text
┌──────────────────────┐
│  Next.js Frontend    │  React UI, routing, presentation
│  TypeScript          │
└──────────┬───────────┘
           │ HTTP/JSON
┌──────────▼───────────┐
│  FastAPI Backend     │  API endpoints, validation, business logic
│  Python              │
└──────────┬───────────┘
           │ SQL / migrations
┌──────────▼───────────┐
│  PostgreSQL          │  Persistent application data
└──────────────────────┘

Docker Compose provides repeatable local orchestration for the services.
```

The frontend is responsible for the user experience and browser-side interaction. The backend will provide the API boundary and centralize domain logic, while PostgreSQL will store durable application data. Docker is intended to standardize local development and service startup across environments.

## Folder Structure

```text
streamsphere/
├── backend/            # FastAPI application, domain logic, and API tests
├── database/            # PostgreSQL schema, migrations, and seed data
├── docker/              # Dockerfiles and local infrastructure configuration
├── docs/                # Architecture, API, and operational documentation
├── frontend/            # Next.js App Router application
│   ├── app/             # Pages, layouts, and global styles
│   ├── public/          # Static frontend assets
│   ├── package.json     # Frontend scripts and dependencies
│   └── package-lock.json
├── .gitignore           # Repository-wide ignore rules
└── README.md            # Project documentation
```

The backend, database, Docker, and documentation directories are reserved for their respective services and supporting assets as implementation progresses.

## Tech Stack

### Application

- **Frontend:** Next.js 16, React 19, TypeScript
- **Styling:** Tailwind CSS 4
- **Backend:** Python, FastAPI
- **Database:** PostgreSQL
- **API format:** JSON over HTTP

### Development and Operations

- **Containerization:** Docker and Docker Compose
- **Frontend quality:** ESLint 9 with the Next.js configuration
- **Dependency management:** npm for the frontend; Python tooling for the backend
- **Configuration:** Environment variables managed through local, uncommitted environment files
- **Hosting target:** Container-compatible infrastructure or Vercel for the frontend

## Setup

### Prerequisites

Install the following tools before starting:

- Git
- Node.js 20.9 or newer
- npm 10 or newer
- Python 3.11 or newer
- Docker Desktop with Docker Compose

### Clone and enter the repository

```bash
git clone <repository-url>
cd streamsphere
```

### Start the frontend

Install the locked frontend dependencies and start the development server:

```bash
cd frontend
npm ci
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in a browser.

### Backend and database

The backend, database schema, and Docker service definitions are part of the repository structure and will be added as those services are implemented. When available, start the complete local stack from the repository root with:

```bash
docker compose up --build
```

Keep secrets and machine-specific configuration in local environment files. Never commit credentials, API keys, or production connection strings. Document required variable names and safe defaults in an environment template when each service is introduced.

## Development Workflow

1. Create a focused branch from the current integration branch.
2. Review the relevant service documentation in [docs/](docs/).
3. Make changes within the appropriate service directory; keep application boundaries clear.
4. Install dependencies using lockfiles and avoid committing generated output.
5. Run frontend checks before opening a pull request:

   ```bash
   cd frontend
   npm run lint
   npm run build
   ```

6. Run backend tests and database migration checks when those services are available.
7. Verify the Docker-based stack and relevant user flows locally.
8. Open a pull request with a concise summary, validation steps, and any migration or configuration notes.

### Recommended commit scope

Keep commits small and service-focused. Separate UI changes, API changes, schema migrations, and infrastructure changes when practical. Database migrations should be reviewed together with the backend code that consumes them.

## Backend Content API

Sprints 4-6 add a movie catalog, engagement features, and an AI-assisted discovery layer to the FastAPI service.

### Database tables

- `users`: authenticated platform users.
- `movies`: catalog records containing title, synopsis, release year, runtime, poster, trailer, maturity rating, and language metadata.
- `genres`: reusable catalog genres such as `Action`, `Comedy`, and `Sci-Fi`.
- `movie_genres`: join table that supports the many-to-many relationship between movies and genres.
- `watchlists`: authenticated users' saved movies, ordered by most recently added.
- `favorites`: authenticated users' favorite movies.
- `ratings`: one 1-5 rating per user per movie.
- `reviews`: user-authored movie reviews with titles, bodies, ratings, and timestamps.
- `watch_progress`: per-user progress tracking for continue watching, including completion state and last watched timestamp.
- `movie_summaries`: cached AI-generated short and long summaries plus themes and target viewer notes for each movie.
- `recommendation_cache`: cached per-user recommendation payloads so the home page and recommendations endpoint can reuse computed results.

When the backend starts, it initializes the schema and automatically seeds 20 sample movies plus the default genre set if the `movies` table is empty.

### API endpoints

Public catalog endpoints:

- `GET /health`
- `GET /movies`
- `GET /movies/trending`
- `GET /movies/{id}`
- `GET /movies/{id}/summary`
- `GET /movies/{id}/reviews`
- `GET /genres`
- `POST /search/ai`

Authenticated write endpoints:

- `POST /auth/register`
- `POST /auth/login`
- `POST /movies`
- `PUT /movies/{id}`
- `DELETE /movies/{id}`
- `POST /movies/{id}/rating`
- `PUT /movies/{id}/rating`
- `DELETE /movies/{id}/rating`
- `POST /movies/{id}/reviews`
- `PUT /reviews/{id}`
- `DELETE /reviews/{id}`
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
- `POST /genres`
- `PUT /genres/{id}`
- `DELETE /genres/{id}`

Admin endpoints:

- `POST /movies/{id}/summary/regenerate`
- `POST /admin/recommendations/recompute`
- `DELETE /admin/recommendations/cache`

`GET /movies` supports:

- `page`
- `page_size`
- `search`
- `sort_by=title|release_year`
- `sort_order=asc|desc`
- `genre`
- `language`

`POST /search/ai` accepts a natural-language query such as `"Funny science fiction movies from the 2020s"` and returns matching movies, model reasoning, and a confidence score.

### AI architecture

Sprint 6 keeps AI logic out of route handlers and organizes it into service modules:

- `ai_provider.py`: provider abstraction with `AIProvider`, `MockAIProvider`, and an `OpenAIProvider` placeholder.
- `recommendation_service.py`: computes or reuses cached personalized recommendations.
- `summary_service.py`: generates and caches movie summaries.
- `search_service.py`: routes natural-language movie search through the provider abstraction.
- `progress_service.py`: manages continue-watching state.
- `trending_service.py`: calculates platform-wide trending and top-rated rankings.
- `home_service.py`: assembles the personalized homepage payload.

The current default provider is the deterministic mock provider. Future OpenAI integration is isolated behind `OpenAIProvider` and configured through environment variables, not hardcoded credentials.

### Caching strategy

- Movie summaries are cached in `movie_summaries` on first request and reused until an admin regenerates them.
- Personalized recommendations are cached in `recommendation_cache` per user and can be recomputed or cleared by an admin.
- Continue-watching state is removed automatically when progress reaches 100%.

### Backend setup and seeding

From `backend/`:

```bash
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```

Seeding is automatic on startup when the catalog is empty. To reseed locally, clear the `movies`, `movie_genres`, and `genres` tables, then restart the backend.

### Test

Backend tests:

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

Backend coverage now includes:

- watchlist CRUD
- favorites CRUD
- rating create/update/delete
- review create/list/update/delete
- profile aggregation
- review permission enforcement
- recommendations and personalized home aggregation
- continue watching progress tracking
- natural-language AI search
- movie summary generation and caching
- admin-only AI maintenance endpoints

## Roadmap

- [x] Establish the FastAPI application and versioned API structure.
- [x] Add PostgreSQL models, migrations, and seed data.
- [ ] Add Docker Compose orchestration for frontend, backend, and database services.
- [x] Build a searchable catalog with genre filters and pagination.
- [x] Add user accounts and JWT-based authentication.
- [x] Add profiles, watchlists, and viewing preferences.
- [ ] Integrate streaming-provider availability and deep links.
- [x] Introduce ratings and personalized recommendations.
- [ ] Add automated accessibility and end-to-end coverage.
- [ ] Configure CI checks, deployment environments, monitoring, and production runbooks.

## License

MIT License.
