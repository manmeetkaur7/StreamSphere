# StreamSphere

StreamSphere is a full-stack movie discovery platform built with Next.js, FastAPI, and PostgreSQL. It allows users to explore movies, search for titles, create an account, manage their profile, and receive personalized movie suggestions.

The platform also includes AI-assisted search to help users discover movies through more natural queries, along with legal demo playback using openly licensed media.

## Live Demo

**Website:** https://stream-sphere-beta.vercel.app

> The deployed backend may take a few seconds to respond when it has been inactive because it is hosted on Render.

## Features

* Browse trending and popular movies
* Search for movies by title
* AI-assisted movie search
* Filter movies by genre and language
* View detailed movie information
* Personalized homepage and recommendations
* Secure user registration and login
* JWT-based authentication
* User profile dashboard
* Personal watchlist and favorites
* Movie ratings and reviews
* Legal demo video playback
* Responsive interface for desktop and mobile devices
* Backend API documentation through FastAPI

## Tech Stack

### Frontend

* Next.js
* React
* TypeScript
* Tailwind CSS

### Backend

* FastAPI
* Python
* SQLAlchemy
* Pydantic
* JWT authentication
* Alembic database migrations

### Database

* PostgreSQL

### Deployment

* Vercel for the frontend
* Render for the backend and database

## Architecture

StreamSphere uses a separate frontend and backend architecture.

The Next.js frontend provides the movie catalog, authentication pages, personalized content, profile dashboard, and AI-assisted search experience.

The FastAPI backend manages authentication, user profiles, movie information, watchlists, ratings, reviews, and recommendation-related requests. SQLAlchemy connects the backend to PostgreSQL, while Alembic manages database migrations.

```text
User
  |
  v
Next.js Frontend
  |
  v
FastAPI REST API
  |
  v
PostgreSQL Database
```

## Project Structure

```text
StreamSphere/
|-- .github/
|   `-- workflows/
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
|-- .env.example
|-- .gitignore
|-- LICENSE
`-- README.md
```

## Local Setup

### Requirements

Before running the project locally, install:

* Node.js
* npm
* Python 3
* PostgreSQL
* Git

### 1. Clone the repository

```bash
git clone https://github.com/manmeetkaur7/StreamSphere.git
cd StreamSphere
```

### 2. Configure PostgreSQL

Create a PostgreSQL database for StreamSphere.

Copy the backend environment example:

```powershell
Copy-Item backend/.env.example backend/.env
```

Open `backend/.env` and provide the required database connection, JWT secret, API keys, and allowed frontend origin.

Do not upload the completed `.env` file to GitHub.

### 3. Start the backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

The backend will be available at:

* API: http://localhost:8000
* API documentation: http://localhost:8000/docs

### 4. Start the frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

The frontend will be available at:

* Website: http://localhost:3000

## Environment Variables

The project uses environment variables for configuration. Refer to the included `.env.example` files for the complete list of required values.

Typical backend configuration includes:

```env
DATABASE_URL=
JWT_SECRET_KEY=
ALLOWED_ORIGINS=
```

The frontend may also require the deployed or local backend URL and any public movie-data configuration used by the application.

Never commit passwords, private API keys, database credentials, or completed `.env` files.

## Testing

Run the backend tests from the repository root:

```powershell
backend\.venv\Scripts\python.exe -m pytest backend\tests
```

Run the frontend checks from the `frontend` directory:

```bash
npm run lint
npm run build
```

## Deployment

The StreamSphere frontend is deployed on Vercel, while the backend and PostgreSQL database are hosted through Render.

Production environment variables are configured directly through the deployment platforms and are not stored in the repository.

For additional deployment information, see the documentation in:

```text
docs/deployment.md
```

## Demo Media Attribution

The video playback demonstration uses footage from *Sintel*, an open movie produced by the Blender Foundation as part of the Durian Open Movie Project.

**Copyright:** © Blender Foundation
**Project website:** https://durian.blender.org/
**License:** Creative Commons Attribution 3.0

The footage is included only to demonstrate StreamSphere’s video playback functionality. StreamSphere does not host or distribute commercial movies.

## Project Status

StreamSphere is a portfolio project developed to demonstrate full-stack development, API integration, authentication, database design, AI-assisted search, personalization, testing, and cloud deployment.

It is a movie discovery application and is not a commercial movie-streaming service.

## Future Improvements

* Improve the recommendation system using additional user activity
* Expand AI-assisted movie discovery
* Add more profile customization options
* Improve accessibility and mobile responsiveness
* Add password recovery and email verification
* Add more automated frontend and backend tests
* Improve loading states and error handling

## Author

**Manmeet Kaur**

* GitHub: https://github.com/manmeetkaur7
* Project: https://github.com/manmeetkaur7/StreamSphere
* Live website: https://stream-sphere-beta.vercel.app/

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

