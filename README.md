# Distributed Job Scheduler

A full-stack distributed job scheduling and execution platform designed to reliably schedule, prioritize, execute, monitor, and recover background jobs across multiple workers.

## Overview

The system provides a centralized scheduler and monitoring dashboard with distributed workers responsible for executing jobs. It supports immediate, delayed, scheduled, and Cron-based jobs with priority handling, retries, worker health monitoring, execution history, logs, metrics, and real-time WebSocket updates.

## Live Application

- Frontend: [DEPLOYED_FRONTEND_URL](https://distributed-job-scheduler-pi.vercel.app)
- Backend: [DEPLOYED_BACKEND_URL](https://distributed-job-scheduler-57j8.onrender.com)

- Documentation: [Project Related Docs](https://github.com/Anurag-1401/distributed-job-scheduler/tree/main/docs)


## API Documentation

### Swagger UI
[Open API Documentation](https://distributed-job-scheduler-57j8.onrender.com/docs)

### ReDoc
[Open ReDoc Documentation](https://distributed-job-scheduler-57j8.onrender.com/redoc)

---

## Key Features

- Immediate, delayed, scheduled, and Cron jobs
- Priority-based job scheduling
- Lower priority value = higher priority
- Queue-based job management
- Multiple distributed workers
- Configurable worker concurrency
- Worker registration and heartbeat monitoring
- Atomic job claiming
- Job execution tracking
- Retry policies
- Abandoned-job recovery
- Job lease management
- Idempotency support
- Execution history and logs
- Real-time WebSocket updates
- Scheduler and worker metrics
- REST API
- Interactive React dashboard
- PostgreSQL persistence
- Redis-based runtime coordination

## Architecture

                         ┌──────────────────────┐
                         │    React Frontend    │
                         │      Dashboard       │
                         └──────────┬───────────┘
                                    │
                              REST / WebSocket
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    FastAPI Backend   │
                         │   API + Scheduler    │
                         └───────┬──────┬───────┘
                                 │      │
                    ┌────────────┘      └────────────┐
                    ▼                                ▼
             ┌──────────────┐                 ┌──────────────┐
             │  PostgreSQL  │                 │    Redis     │
             │   Database   │                 │   Runtime    │
             └──────────────┘                 └──────────────┘
                                 │
                                 ▼
                    ┌─────────────────────────┐
                    │   Distributed Workers   │
                    │ Worker 1 ... Worker N   │
                    └─────────────────────────┘

---

## Job Lifecycle

CREATED
   │
   ├──► SCHEDULED ──► QUEUED
   │
   └──► QUEUED
          │
          ▼
        CLAIMED
          │
          ▼
        RUNNING
       /       \
      ▼         ▼
 COMPLETED     FAILED
                 │
                 ▼
               RETRY
                 │
                 └────► QUEUED


---

## Supported Job Types

- Immediate — executed as soon as a worker is available
- Delayed — executed after a specified delay
- Scheduled — executed at a specified date and time
- Cron — repeatedly generated according to a Cron expression and timezone
- Batch — creates and schedules multiple jobs as a single batch request

  ### Batch

Creates multiple jobs through a single API request.

Example:

```json
[
  {
    "task": "echo",
    "message": "job A"
  },
  {
    "task": "echo",
    "message": "job B"
  }
]
```

## Job States

- QUEUED
- SCHEDULED
- CLAIMED
- RUNNING
- COMPLETED
- FAILED
- RETRYING
- DEAD_LETTER
- CANCELLED

  
---

## Worker System

Workers independently register with the backend and continuously:

1. Register with the scheduler
2. Maintain an online status
3. Send periodic heartbeats
4. Poll for available jobs
5. Claim eligible jobs
6. Execute tasks
7. Report completion or failure
8. Participate in abandoned-job recovery


## Worker Lifecycle

```text
START
  ↓
REGISTER
  ↓
HEARTBEAT
  ↓
POLL
  ↓
CLAIM
  ↓
EXECUTE
  ↓
SUCCESS / FAILURE
  ↓
REPORT RESULT
  ↓
POLL AGAIN

```

## Real-Time Updates

The frontend receives job state changes through WebSockets.
-WebSocket endpoint:/api/v1/jobs/ws
-Supported events:
  - job.created
  - job.updated

This allows job status and execution information to be reflected in the dashboard without manual page refreshes.

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite |
| Backend | FastAPI |
| ORM | SQLAlchemy |
| Database | PostgreSQL |
| Cache / Coordination | Redis |
| Authentication | JWT |
| Migrations | Alembic |
| Testing | Pytest + Vitest |
| Real-time | WebSocket |

---

## Project Structure

distributed-job-scheduler/
│
├── backend/
│   ├── app/
│   ├── alembic/
│   ├── docs/
│   ├── scripts/
│   ├── tests/
│   ├── run.py
│   ├── scheduler.py
│   ├── worker.py
│   ├── alembic.ini
│   ├── pyproject.toml
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── ...
│
├── docs/
│   ├── architecture.md
│   ├── database-design.md
│   ├── design-decisions.md
│   ├── api.md
│   ├── testing.md
│   └── diagrams/
│
└── README.md

---

## Backend Setup

Prerequisites:
- Python 3.11+
- PostgreSQL
- Redis or Redis-compatible service
- pip

```bash
- cd backend
python -m venv .venv

- Windows: .venv\Scripts\activate

- Install dependencies:pip install -r requirements.txt

- Run migrations:python -m alembic upgrade head

- Start the backend:python -m run

```

---

## Frontend Setup

```bash
- cd frontend
npm install
npm run dev

-Production build:npm run build

```

---

## Environment Configuration

The backend requires environment variables for database, Redis, authentication, scheduler, worker, heartbeat, lease, and concurrency configuration.

Example:
```bash
- DATABASE_URL=postgresql+asyncpg://user:password@host:5432/database
- REDIS_URL=redis://host:6379
- SECRET_KEY=your-secret-key
- SCHEDULER_INTERVAL_SECONDS=1
- POLL_INTERVAL_SECONDS=1
- HEARTBEAT_INTERVAL_SECONDS=5
- LEASE_TIMEOUT_SECONDS=30
- MAX_CONCURRENCY=5

- The frontend uses:VITE_API_BASE_URL=http://localhost:8000

For production, VITE_API_BASE_URL should point to the deployed backend API.

```
---

## Docker Setup

The Distributed Job Scheduler can be run completely using Docker Compose. Docker starts the frontend, backend, PostgreSQL database, and Redis services together.

### Prerequisites

Make sure you have installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Docker Compose (included with Docker Desktop)

Verify the installation:

```bash
docker --version
docker compose version
```

```bash
1. Clone the Repository
git clone <repository-url>
cd distributed-job-scheduler

2. Start the Application
Build and start all services:
docker compose up --build

3. Stop the Application
docker compose down
```

## Testing

- Run backend tests:
cd backend
pytest

---

## API Documentation

Local Swagger documentation:

http://localhost:8000/api/docs

Local ReDoc documentation:

http://localhost:8000/api/redoc

---

## Production Deployment

The application can be deployed using separate services for the frontend, backend, PostgreSQL, Redis, and workers.

                         ┌──────────────────┐
                         │ React Frontend   │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │ FastAPI Backend  │
                         └──────┬─────┬─────┘
                                │     │
                                ▼     ▼
                         PostgreSQL  Redis
                                │
                                ▼
                       Distributed Workers
                       Worker 1 ... Worker N

Production deployment requires:

- PostgreSQL database
- Redis or Redis-compatible service
- Backend API service
- One or more worker processes
- Frontend hosting
- Environment variables
- Database migrations

Sensitive credentials must be stored as deployment environment variables and must not be committed to the repository.


---

## Known Limitations

- Workers currently execute only the task types registered by the worker runtime.
- Arbitrary user-provided Python code is never executed.
- Redis is used for runtime coordination rather than durable job persistence.
- Production deployment requires externally managed PostgreSQL and Redis instances.

---
