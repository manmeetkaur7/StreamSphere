# StreamSphere Security Notes

## Authentication

- REST authentication uses JWT bearer tokens.
- WebSocket notifications use the same JWT validation path.
- Tokens are signed with `JWT_SECRET_KEY` and `JWT_ALGORITHM`.
- Inactive users are denied login and protected-route access.

## Authorization

- `get_current_user` protects authenticated routes.
- `require_admin` protects admin-only routes.
- Ownership checks are enforced on user-scoped resources such as reviews and notifications.
- WebSocket notification connections are bound to the authenticated user only.

## Password Storage

- New passwords are hashed with Argon2.
- Legacy bcrypt hashes remain verifiable for compatibility.
- Plaintext passwords are never stored or returned by any API response.
- Reasonable validation rules are enforced:
  - minimum length 8
  - maximum 72 bytes
  - username format restrictions remain unchanged

## Secret Management

- Secrets are loaded from environment variables.
- Real `.env` files must never be committed.
- Example configuration is kept in `.env.example` and `backend/.env.example`.
- No production secrets are stored in CI configuration.

## Rate Limiting

- Rate limiting is applied at middleware level.
- Redis is preferred; in-memory fallback is available.
- `429` responses include a safe error payload, limit headers, and `Retry-After`.

## Input Validation

- FastAPI and Pydantic validate request bodies and query inputs.
- Structured `422` error responses include a safe message and request ID.
- SQLAlchemy models enforce important constraints such as rating bounds and uniqueness on favorites, watchlists, ratings, and progress.

## CORS

- Allowed origins are environment-driven.
- Local development origins are added explicitly for `localhost` and `127.0.0.1`.
- The default configuration is appropriate for local development but should be narrowed in production.

## Security Headers

The application configures:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Content-Security-Policy` from environment configuration

The default CSP is pragmatic for the current Next.js development flow and external media usage. Tighten it further before production rollout if inline scripts/styles are removed.

## Error Handling

- Safe JSON error responses include:
  - `detail`
  - `error.code`
  - `error.message`
  - `error.request_id`
- Internal stack traces are logged server-side and not exposed to clients.
- SQL errors, secrets, and environment contents are not returned to clients.

## Logging Rules

- Structured request logs include request ID, path, method, status, duration, and client IP.
- Sensitive data such as passwords, JWTs, API keys, and auth headers must not be logged.
- Activity metadata sanitization drops keys like `password`, `token`, `jwt`, `authorization`, `api_key`, and `secret`.

## Known Limitations

- JWTs are short-lived access tokens only; refresh tokens are not implemented.
- Token revocation and device/session management are not implemented.
- Password rehash-on-login for legacy bcrypt users is not yet implemented.
- CSP remains permissive enough for local development and current frontend behavior.
- Background tasks are not yet durable across process crashes because they still use FastAPI `BackgroundTasks`.

## Future Improvements

- Add refresh tokens and explicit token revocation
- Add session/device management
- Rehash legacy bcrypt users to Argon2 during login
- Tighten CSP after removing remaining inline requirements
- Move background work to a durable queue
- Add audit logs for admin mutations
- Add secret scanning to CI and pre-commit hooks
