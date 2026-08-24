# Load Testing

This directory contains a lightweight Locust setup for StreamSphere.

## Scenarios

- `GET /movies`
- `GET /movies/trending`
- `GET /home` when credentials are provided
- `GET /profile` when credentials are provided
- `POST /auth/login` during startup when credentials are provided
- `POST /search/ai` with a safe, low-frequency query

## Run Locally

From the repository root:

```powershell
backend\.venv\Scripts\locust.exe -f load-tests\locustfile.py --headless --users 5 --spawn-rate 1 --run-time 30s
```

Optional environment variables:

```powershell
$env:STREAMSPHERE_BASE_URL = "http://127.0.0.1:8000"
$env:STREAMSPHERE_LOADTEST_USERNAME = "your-user@example.com"
$env:STREAMSPHERE_LOADTEST_PASSWORD = "your-password"
```

## Notes

- This is intended for smoke and benchmark-style runs, not destructive stress testing.
- Keep user counts small on local machines.
- If auth credentials are not provided, authenticated tasks are skipped automatically.
