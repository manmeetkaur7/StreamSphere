# StreamSphere

StreamSphere is a modern web application for discovering, organizing, and enjoying streaming content in one focused experience. The project is built with the Next.js App Router and is structured for incremental product development and production deployment.

## Tech Stack

- **Framework:** Next.js 16 with the App Router
- **Language:** TypeScript
- **UI:** React 19
- **Styling:** Tailwind CSS 4
- **Linting:** ESLint 9 with the Next.js configuration
- **Package manager:** npm
- **Deployment:** Compatible with Vercel and standard Node.js hosting

## Folder Structure

```text
frontend/
├── app/                  # App Router pages, layouts, and global styles
│   ├── globals.css       # Global styles and Tailwind layers
│   ├── layout.tsx        # Root layout and application metadata
│   └── page.tsx          # Home page
├── public/               # Static assets served from the site root
├── .gitignore            # Repository and environment exclusions
├── next.config.ts        # Next.js configuration
├── package.json          # Scripts and dependencies
├── package-lock.json     # Reproducible npm dependency lockfile
├── postcss.config.mjs    # PostCSS configuration
└── tsconfig.json         # TypeScript configuration
```

## Getting Started

### Prerequisites

- Node.js 20.9 or newer
- npm 10 or newer (included with current Node.js releases)

### Installation

Install the locked dependency versions from the project directory:

```bash
npm ci
```

### Run locally

Start the development server:

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in a browser.

### Validate and build

Run the production checks and build locally before deployment:

```bash
npm run lint
npm run build
npm run start
```

Environment-specific values should be stored in a local `.env.local` file and must never be committed. Add required variable names and safe, non-secret defaults to `.env.example`.

## Future Roadmap

- Add a searchable catalog with genre, provider, and availability filters.
- Introduce user accounts, profiles, and personalized watchlists.
- Connect streaming-provider APIs for availability and deep links.
- Add ratings, recommendations, and activity-based personalization.
- Expand automated testing, accessibility coverage, and observability.
- Add a production container workflow and continuous integration checks.
