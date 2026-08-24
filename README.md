Distributed Job Scheduler

A full-stack distributed job scheduling and execution platform for creating, scheduling, executing, monitoring, and recovering background jobs across multiple workers.

The system provides a centralized backend for job scheduling and management, distributed worker processes for execution, PostgreSQL for persistent storage, Redis for runtime coordination, and a React dashboard for monitoring jobs and system activity in real time.

\---

Project Description

Distributed Job Scheduler demonstrates a reliable distributed background job processing system.

The platform supports immediate, delayed, scheduled, and Cron-based jobs. Jobs can be assigned priorities, executed concurrently by multiple workers, retried after failures, and recovered when a worker becomes unavailable.

The dashboard provides job lifecycle visualization, execution history, logs, worker information, queue management, and system metrics. WebSockets provide real-time job status updates without requiring manual page refreshes.

\---

Key Features

Immediate, delayed, scheduled, and Cron-based jobs

Timezone-aware Cron scheduling

Priority-based scheduling

Queue-based job management

Distributed worker execution

Configurable worker concurrency

Worker registration and health monitoring

Worker heartbeat mechanism

Atomic job claiming

Job lease management

Retry policies

Abandoned-job recovery

Idempotency support

Job execution history and logs

Job lifecycle tracking

Scheduler and worker monitoring

System metrics

REST API

Real-time WebSocket updates

React monitoring dashboard

PostgreSQL persistence

Redis runtime coordination

\---

System Architecture

\`\`\`text

React Frontend

|

REST / WebSocket

|

v

FastAPI Backend

/ \\

/ \\

v v

PostgreSQL Redis

Persistence Runtime/Queue

|

v

Distributed Workers

Worker 1 ... Worker N

\`\`\`

The frontend communicates with the FastAPI backend through REST APIs and WebSockets.

The backend manages job scheduling, queues, workers, execution state, persistence, recovery, and monitoring.

PostgreSQL stores persistent application data including jobs, queues, workers, executions, schedules, and logs.

Redis is used for runtime coordination and production deployment.

Multiple worker processes can operate independently and execute jobs concurrently.

\---

Job Lifecycle

\`\`\`text

CREATED

|

+----> SCHEDULED ----> QUEUED

|

+----> QUEUED

|

v

CLAIMED

|

v

RUNNING

/ \\

v v

COMPLETED FAILED

|

v

RETRY

|

v

QUEUED

\`\`\`

\---

Supported Job Types

Immediate

The job becomes available for execution immediately after creation.

Delayed

The job becomes available after a specified delay.

Scheduled

The job is executed at a specified date and time.

Cron

A recurring schedule is created using a Cron expression and timezone. The scheduler generates executable jobs according to the configured schedule.

\---

Priority Scheduling

Jobs support positive integer priorities. Lower numeric values represent higher priority.

\`\`\`text

1 Highest Priority

2

3

4

5 Lower Priority

\`\`\`

\---

Distributed Worker System

Workers are independent execution processes.

Each worker:

Registers with the backend.

Becomes available for job execution.

Sends periodic heartbeats.

Polls for available jobs.

Claims eligible jobs.

Executes tasks.

Records execution results.

Updates job state.

Participates in abandoned-job recovery.

Worker configuration includes worker ID, worker key, status, maximum concurrency, current job count, and last heartbeat timestamp.

Multiple workers can operate simultaneously, allowing the system to distribute workload across execution processes.

\---

Reliability and Recovery

Job Claiming

Workers claim jobs before execution so that the same job is not normally processed simultaneously by multiple workers.

Worker Heartbeats

Workers periodically update heartbeat information so the system can determine whether a worker is active.

Job Leases

Jobs can be protected by execution leases. If a worker stops processing a job and the lease expires, the job can be considered abandoned.

Abandoned Job Recovery

The recovery process identifies abandoned jobs and makes them available for execution again according to configured recovery and retry rules.

Retry Handling

Failed jobs can be retried according to their configured retry policy.

Idempotency

Idempotency keys prevent duplicate job creation when the same request is submitted more than once.

\---

Real-Time Updates

The backend exposes the following WebSocket endpoint:

\`\`\`text

/api/v1/jobs/ws

\`\`\`

Supported events include:

\`\`\`text

job.created

job.updated

\`\`\`

The frontend listens for these events and updates the dashboard in real time.

\---

Monitoring

The dashboard provides visibility into:

Job state

Job ID

Queue

Priority

Attempts

Worker

Created time

Scheduled time

Claimed time

Retry information

Job lifecycle

Payload

Execution history

Execution results

Job logs

Worker status

Worker heartbeat

Worker concurrency

Scheduler activity

System metrics

\---

Technology Stack

LayerTechnology

FrontendReact, JavaScript, Vite

BackendPython, FastAPI

ORMSQLAlchemy

DatabasePostgreSQL

Database Driverasyncpg

MigrationsAlembic

ValidationPydantic

Runtime CoordinationRedis

Async Executionasyncio

Real-Time CommunicationWebSockets

Testingpytest

\---

Repository Structure

\`\`\`text

distributed-job-scheduler/

|

├── backend/

| ├── app/

| ├── alembic/

| ├── tests/

| ├── requirements.txt

| └── README.md

|

├── frontend/

| ├── src/

| ├── public/

| ├── package.json

| └── README.md

|

└── README.md

\`\`\`

\---

Backend Setup

Prerequisites

Python 3.11+

PostgreSQL

Redis or Redis-compatible service

pip

Installation

\`\`\`bash

cd backend

python -m venv .venv

\`\`\`

Windows:

\`\`\`bash

.venv\\Scripts\\activate

\`\`\`

Install dependencies:

\`\`\`bash

pip install -r requirements.txt

\`\`\`

Run database migrations:

\`\`\`bash

python -m alembic upgrade head

\`\`\`

Start the backend:

\`\`\`bash

python -m run

\`\`\`

\---

Frontend Setup

Prerequisites

Node.js

npm

Installation

\`\`\`bash

cd frontend

npm install

\`\`\`

Start the development server:

\`\`\`bash

npm run dev

\`\`\`

Create a production build:

\`\`\`bash

npm run build

\`\`\`

\---

Environment Configuration

Backend configuration is provided through environment variables.

Example:

\`\`\`env

DATABASE\_URL=postgresql+asyncpg://user:password@host:5432/database

REDIS\_URL=redis://host:6379

SECRET\_KEY=your-secret-key

SCHEDULER\_INTERVAL\_SECONDS=1

POLL\_INTERVAL\_SECONDS=1

HEARTBEAT\_INTERVAL\_SECONDS=5

LEASE\_TIMEOUT\_SECONDS=30

MAX\_CONCURRENCY=5

\`\`\`

Frontend configuration:

\`\`\`env

VITE\_API\_BASE\_URL=http://localhost:8000

\`\`\`

Production deployments should use the deployed PostgreSQL and Redis service URLs instead of localhost services.

\---

API Documentation

When the backend is running:

\`\`\`text

http://localhost:8000/api/docs

\`\`\`

Alternative documentation:

\`\`\`text

http://localhost:8000/api/redoc

\`\`\`

\---

Database Migrations

Apply existing migrations:

\`\`\`bash

python -m alembic upgrade head

\`\`\`

Create a new migration:

\`\`\`bash

python -m alembic revision --autogenerate -m "description"

\`\`\`

\---

Testing

Run backend tests:

\`\`\`bash

cd backend

pytest

\`\`\`

\---

Production Deployment

The application can be deployed using separate services for the frontend, backend, PostgreSQL, Redis, and workers.

\`\`\`text

Frontend

|

v

Backend API

|

+---- PostgreSQL

|

+---- Redis

|

+---- Worker 1

+---- Worker 2

+---- Worker N

\`\`\`

Production deployment requires PostgreSQL, Redis or a Redis-compatible service, the backend service, one or more worker processes, frontend hosting, environment configuration, and database migrations.

Sensitive credentials must be stored in deployment environment variables and must not be committed to the repository.

\---

Project Objective

The objective of this project is to implement a reliable distributed job scheduling platform capable of scheduling, prioritizing, executing, monitoring, retrying, and recovering background jobs across multiple workers while maintaining persistent execution data and providing real-time system visibility.
