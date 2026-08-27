# StreamSphere Interview Guide

## What is StreamSphere?

StreamSphere is a full-stack movie discovery platform. Users browse a catalog, save favorites and watchlists, rate and review movies, receive recommendations, use natural-language search, and see notifications and personal insights.

## Why did you build it?

It is a focused way to demonstrate product work across a modern frontend, a relational API, authentication, real-time UX, and pragmatic AI integration without relying on a proprietary streaming catalog.

## What is the architecture?

Next.js handles the user interface. FastAPI exposes REST and WebSocket endpoints. SQLAlchemy maps the PostgreSQL schema. Services own recommendations, analytics, cache behavior, notifications, AI calls, and background work. See [architecture-summary.md](architecture-summary.md).

## Why FastAPI, PostgreSQL, and Next.js?

FastAPI provides typed request/response contracts and strong dependency injection. PostgreSQL fits the relational connections among users, movies, genres, and engagement data. Next.js provides server-rendered catalog pages and focused client interactivity in one TypeScript codebase.

## How does JWT authentication work?

Registration hashes passwords with Argon2. Login returns a signed, expiring JWT. Protected REST routes resolve the token to an active user; the notifications WebSocket also validates the token. Existing bcrypt hashes remain verifiable for migration compatibility.

## How do recommendations and AI search work?

Recommendations combine favorites, ratings, watchlist activity, catalog quality, and recency. AI search and summaries call an `AIProvider` abstraction. The current mock provider uses deterministic catalog signals, while resilience code adds timeouts, retries, caching, and safe fallback responses.

## How do caching and notifications work?

Redis is used for cache and rate limiting when configured. If it is unavailable, the application falls back to local in-memory implementations and reports a degraded health state. Notifications use WebSockets when connected and REST polling otherwise.

## How would you scale it?

Run multiple API instances behind a load balancer, move PostgreSQL and Redis to managed services, and extract long-running AI and notification work to a durable queue. The modular service layer is designed to make those changes incremental.

## Hardest technical problem and tradeoffs

The main challenge was keeping personalization responsive while engagement data changes. The project uses targeted invalidation and background refresh rather than a complex event pipeline. That is easier to operate for this scale, at the cost of eventually consistent recommendation updates.

## What would you improve next?

Implement the real OpenAI provider, add password reset delivery through an email provider, introduce role management beyond a boolean admin flag, and add deployed monitoring and end-to-end browser tests.
