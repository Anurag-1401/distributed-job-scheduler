# Frontend API contract

**Status:** Backend OpenAPI is not present in this repository yet.  
Endpoints below are mapped from the backend product brief (not invented beyond that spec). Marked **assumed** until the FastAPI app exists.

Base URL: `VITE_API_BASE_URL` (example: `http://localhost:8000`).

Auth: `Authorization: Bearer <access_token>` on authenticated routes.

Error envelope:

```json
{
  "error": {
    "code": "QUEUE_NOT_FOUND",
    "message": "Queue does not exist",
    "details": {}
  }
}
```

Pagination (list endpoints): `page` (1-based), `limit`, optional `sort`, `order` (`asc`|`desc`).

Response list shape (assumed):

```json
{
  "items": [],
  "total": 0,
  "page": 1,
  "limit": 20
}
```

## Health

| UI | Method | Path | Confirmed |
| --- | --- | --- | --- |
| Readiness / settings | GET | `/health` | specified |
| Readiness | GET | `/ready` | specified |

## Auth

| UI | Method | Path | Body / notes |
| --- | --- | --- | --- |
| Register | POST | `/api/v1/auth/register` | `{ email, password, name }` |
| Login | POST | `/api/v1/auth/login` | `{ email, password }` → `{ access_token, token_type }` |
| Current user | GET | `/api/v1/auth/me` | user + memberships |

Token storage: access token in `localStorage` (`scheduler.access_token`) because the brief specifies JWT in the login response, not httpOnly cookies. No secrets in frontend code.

## Organizations (required for project isolation)

| UI | Method | Path |
| --- | --- | --- |
| Org picker / settings | GET | `/api/v1/organizations` |
| Create org | POST | `/api/v1/organizations` `{ name }` |
| Org detail | GET | `/api/v1/organizations/{id}` |

## Projects

| UI | Method | Path |
| --- | --- | --- |
| List / create form | GET/POST | `/api/v1/projects` |
| Detail / edit / delete | GET/PATCH/DELETE | `/api/v1/projects/{id}` |

POST body: `{ organization_id, name, description }`.

## Queues

| UI | Method | Path |
| --- | --- | --- |
| List / create | GET/POST | `/api/v1/queues` |
| Detail / edit / delete | GET/PATCH/DELETE | `/api/v1/queues/{id}` |
| Pause | POST | `/api/v1/queues/{id}/pause` |
| Resume | POST | `/api/v1/queues/{id}/resume` |

Query: `project_id`, `status`.  
POST body: `{ project_id, name, priority, concurrency_limit, retry_policy }`.

Retry policy: `{ strategy: FIXED|LINEAR|EXPONENTIAL, max_attempts, base_delay_seconds, max_delay_seconds }`.

## Jobs

| UI | Method | Path |
| --- | --- | --- |
| Explorer / create | GET/POST | `/api/v1/jobs` |
| Detail | GET | `/api/v1/jobs/{id}` |
| Retry | POST | `/api/v1/jobs/{id}/retry` |
| Cancel | POST | `/api/v1/jobs/{id}/cancel` |
| Executions | GET | `/api/v1/jobs/{id}/executions` |
| Logs | GET | `/api/v1/jobs/{id}/logs` |
| Batch create | POST | `/api/v1/jobs/batch` |

GET filters: `status`, `queue_id`, `priority`, `worker_id`, `created_after`, `created_before`, `q` (search), `sort`, `order`, `page`, `limit`.  
Idempotency: optional header `Idempotency-Key`.

Job types: `IMMEDIATE`, `DELAYED`, `SCHEDULED`, `CRON`, `BATCH`.

## Dead letter

| UI | Method | Path |
| --- | --- | --- |
| DLQ list | GET | `/api/v1/dead-letter-jobs` |
| Inspect | GET | `/api/v1/dead-letter-jobs/{id}` |
| Retry | POST | `/api/v1/dead-letter-jobs/{id}/retry` |
| Delete/archive | DELETE | `/api/v1/dead-letter-jobs/{id}` |

## Workers

| UI | Method | Path |
| --- | --- | --- |
| List | GET | `/api/v1/workers` |
| Detail | GET | `/api/v1/workers/{id}` |

Status values displayed: `ONLINE`, `OFFLINE`, `DRAINING`.

## Metrics

| UI | Method | Path |
| --- | --- | --- |
| Dashboard | GET | `/api/v1/stats` |

Assumed payload includes queue/job/worker totals, throughput, average execution time, and time-series for charts.

## Delivery / auth notes for UI

- Job execution is **at-least-once** on the backend; Retry may create a new attempt, not an exactly-once replay.
- 401 clears the local token and redirects to `/login`.
