# Architecture Summary

StreamSphere is a modular full-stack movie discovery application. It is intentionally a modular monolith: related capabilities are separated into focused API, schema, model, and service modules while remaining simple to deploy and reason about.

## Runtime shape

```text
Next.js + TypeScript
        |
FastAPI routes -> services -> SQLAlchemy -> PostgreSQL
        |              |
        |              +-> AI provider abstraction (mock today)
        +-> WebSocket notifications
        +-> Redis cache/rate limit, with in-memory fallback
```

The Next.js App Router frontend server-renders catalog pages and uses client components for authenticated interaction, notifications, profile analytics, and AI search. FastAPI exposes the REST and WebSocket contracts, and SQLAlchemy owns relational persistence.

## Core decisions

- PostgreSQL holds users, movies, genres, engagement records, summaries, recommendation cache entries, analytics events, and notifications. Foreign keys and targeted indexes support the read patterns used by catalog, profile, and analytics views.
- JWT access tokens authenticate API and WebSocket requests. Passwords use Argon2 for new hashes while legacy bcrypt hashes remain supported.
- Cache and recommendation invalidation live in services rather than routes. Redis improves cross-process behavior; in-memory fallback preserves availability during a Redis outage.
- AI is behind an `AIProvider` interface. The mock provider makes demos and tests deterministic; resilience wrappers time out, retry, and return safe fallback content when a provider fails.
- Background task dispatching handles recommendation refreshes, notifications, and summary work after synchronous user actions complete.
- WebSocket notifications deliver live updates with REST polling as the browser fallback.
- Structured request logs, request IDs, `/health`, `/metrics`, security headers, and rate limiting provide operational visibility and baseline safety.

## Scaling approach

The application can scale horizontally behind a load balancer when PostgreSQL and Redis are managed shared services. Redis should be enabled for consistent cache and rate-limit state across API instances. Longer AI jobs and notification delivery are the natural first candidates for an external job queue; the existing service boundaries make that extraction incremental.
