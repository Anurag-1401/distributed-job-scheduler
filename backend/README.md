# Distributed Job Scheduler Backend

A production-inspired distributed job scheduler built with **Python + FastAPI + SQLAlchemy + PostgreSQL + Redis**.

## Important runtime model

The project intentionally runs the complete application with **one Python/FastAPI process**:

```text
python run.py
     |
     +--> Alembic migrations -> Supabase PostgreSQL
     |
     +--> Uvicorn / FastAPI
             |
             +--> REST API
             +--> Scheduler background task
             +--> Logical worker 1
             +--> Logical worker 2
             +--> Logical worker 3
             +--> Worker heartbeats
             +--> Recovery loop
             +--> Redis coordination
```

You do **not** need separate `api`, `worker`, and `scheduler` processes for local development or the internship demo.

`WORKER_COUNT=3` creates three logical workers inside the same async Python process. PostgreSQL row locking is still used for atomic claims, so the claiming logic is concurrency-safe. For a later production deployment, the same worker implementation can be split into multiple processes/containers without redesigning the job model.

## Infrastructure

- **Supabase PostgreSQL** — durable source of truth.
- **Redis** — scheduler leadership/coordination and infrastructure readiness.
- **FastAPI/Uvicorn** — API plus scheduler and worker runtime.
- **Alembic** — database migrations.

## Setup

### 1. Create the environment

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS/Linux:

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure `.env`

```bash
copy .env.example .env
```

or:

```bash
cp .env.example .env
```

Set your Supabase `DATABASE_URL` and Redis `REDIS_URL`.

For Supabase, SSL is enabled by default. If you use a pooler URL, keep the complete connection string supplied by Supabase.

### 4. Start everything

```bash
python run.py
```

This single command:

1. runs `alembic upgrade head`;
2. starts Uvicorn;
3. starts the scheduler;
4. starts the configured logical workers;
5. starts heartbeat/recovery loops;
6. keeps the REST API available.

### 5. Open the API

- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- Health: `http://localhost:8000/health`
- Readiness: `http://localhost:8000/ready`

Frontend should use:

```env
VITE_API_BASE_URL=http://localhost:8000
```

## Redis options

### Local Redis

```env
REDIS_URL=redis://localhost:6379/0
```

### Managed Redis

Use your provider's TLS URL, for example:

```env
REDIS_URL=rediss://default:PASSWORD@HOST:6379
```

No Redis Docker container is required by this project.

## API ↔ Frontend contract

The backend matches the polished frontend endpoints:

```text
POST /api/v1/auth/register
POST /api/v1/auth/login
GET  /api/v1/auth/me

GET  /api/v1/organizations
POST /api/v1/organizations

GET  /api/v1/projects
POST /api/v1/projects
GET  /api/v1/projects/{id}
PATCH /api/v1/projects/{id}
DELETE /api/v1/projects/{id}

GET  /api/v1/queues
POST /api/v1/queues
GET  /api/v1/queues/{id}
PATCH /api/v1/queues/{id}
POST /api/v1/queues/{id}/pause
POST /api/v1/queues/{id}/resume

GET  /api/v1/jobs
POST /api/v1/jobs
POST /api/v1/jobs/batch
GET  /api/v1/jobs/{id}
POST /api/v1/jobs/{id}/retry
POST /api/v1/jobs/{id}/cancel
GET  /api/v1/jobs/{id}/executions
GET  /api/v1/jobs/{id}/logs

GET  /api/v1/workers
GET  /api/v1/workers/{id}
GET  /api/v1/workers/{id}/jobs

GET  /api/v1/dlq
GET  /api/v1/dlq/{id}
POST /api/v1/dlq/{id}/retry
DELETE /api/v1/dlq/{id}

GET /api/v1/metrics/overview
```

## Reliability model

- Atomic claims use PostgreSQL row locking with `SKIP LOCKED`.
- Queue concurrency is checked while the queue row is locked, so the limit applies across all logical workers.
- Execution semantics are **at-least-once**, not exactly-once.
- Retry policies support fixed, linear, and exponential backoff with optional jitter.
- Worker heartbeats are persisted.
- Stale claimed/running jobs are recovered after the lease timeout.
- Failed jobs eventually enter the DLQ.
- Idempotency keys protect repeated API submissions.
- Cron scheduling is timezone-aware.
- Redis provides scheduler leadership so multiple application instances do not all promote schedules simultaneously.

## Demo task types

Supported safe built-in tasks are defined in `app/tasks.py`:

- `echo`
- `sleep_task`
- `email_simulation`
- `data_processing`
- `http_request`

The API never executes arbitrary Python supplied by a client.

## Tests

```bash
pytest
```

For concurrency tests, point the test configuration at a real PostgreSQL database when required.
