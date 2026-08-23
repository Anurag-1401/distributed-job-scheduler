# Frontend API Contract

The frontend expects a versioned FastAPI API rooted at the host configured by `VITE_API_BASE_URL`.

## Authentication
- `POST /api/v1/auth/register`
- `POST /api/v1/auth/login`
- `GET /api/v1/auth/me`
- `POST /api/v1/auth/logout`

## Organizations
- `GET /api/v1/organizations`
- `POST /api/v1/organizations`
- `GET /api/v1/organizations/{id}`
- `PATCH /api/v1/organizations/{id}`

## Projects
- `GET /api/v1/projects`
- `POST /api/v1/projects`
- `GET /api/v1/projects/{id}`
- `PATCH /api/v1/projects/{id}`
- `DELETE /api/v1/projects/{id}`

## Queues
- `GET /api/v1/queues`
- `POST /api/v1/queues`
- `GET /api/v1/queues/{id}`
- `PATCH /api/v1/queues/{id}`
- `POST /api/v1/queues/{id}/pause`
- `POST /api/v1/queues/{id}/resume`

## Jobs
- `GET /api/v1/jobs`
- `POST /api/v1/jobs`
- `POST /api/v1/jobs/batch`
- `GET /api/v1/jobs/{id}`
- `POST /api/v1/jobs/{id}/retry`
- `POST /api/v1/jobs/{id}/cancel`
- `GET /api/v1/jobs/{id}/executions`
- `GET /api/v1/jobs/{id}/logs`

## Workers
- `GET /api/v1/workers`
- `GET /api/v1/workers/{id}`
- `GET /api/v1/workers/{id}/jobs`

## DLQ
- `GET /api/v1/dlq`
- `GET /api/v1/dlq/{id}`
- `POST /api/v1/dlq/{id}/retry`
- `DELETE /api/v1/dlq/{id}`

## Metrics and health
- `GET /api/v1/metrics/overview`
- `GET /api/v1/metrics/queues/{id}`
- `GET /api/v1/metrics/workers/{id}`
- `GET /health`
- `GET /ready`

List responses should use `{ items, page, limit, total }`. Errors should preferably use `{ error: { code, message } }`.
