# Distributed Job Scheduler

A full-stack distributed job scheduling and execution platform designed to reliably schedule, prioritize, execute, monitor, and recover background jobs across multiple workers.

## Overview

The system provides a centralized scheduler and monitoring dashboard with distributed workers responsible for executing jobs. It supports immediate, delayed, scheduled, and Cron-based jobs with priority handling, retries, worker health monitoring, execution history, logs, metrics, and real-time WebSocket updates.

## Key Features

- Immediate, delayed, scheduled, and Cron jobs
- Priority-based job scheduling
- Positive priority values with lower value = higher priority
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
- Execution history
- Job logs
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
             │  Database    │                 │    Runtime   │
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
 -- Immediate — executed as soon as a worker is available
 -- Delayed — executed after a specified delay
 -- Scheduled — executed at a specified date and time
 -- Cron — repeatedly generated according to a Cron expression and timezone
 -- Worker System

-> Workers independently register with the backend and continuously:

Register with the scheduler
Maintain an online status
Send heartbeats
Poll for available jobs
Claim jobs
Execute tasks
Report completion or failure
Participate in abandoned-job recovery

## Technology Stack

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

## Project Structure

distributed-job-scheduler/
│
├── backend/
│   ├── app/
│   ├── alembic/
│   ├── tests/
│   ├── requirements.txt
│   └── README.md
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── README.md
│
└── README.md

---

-- Backend Setup
cd backend
python -m venv .venv

Windows:
.venv\Scripts\activate

Install dependencies:
pip install -r requirements.txt
Run migrations:
python -m alembic upgrade head

Start the backend:
python -m run

-- Frontend Setup
cd frontend
npm install
npm run dev

Production build:
npm run build

-- Environment Configuration
The backend requires environment variables for database, Redis, authentication, scheduler, worker, heartbeat, lease, and concurrency configuration.
Example:

DATABASE_URL=postgresql+asyncpg://...
REDIS_URL=redis://...
SECRET_KEY=...

SCHEDULER_INTERVAL_SECONDS=1
POLL_INTERVAL_SECONDS=1
HEARTBEAT_INTERVAL_SECONDS=5
LEASE_TIMEOUT_SECONDS=30
MAX_CONCURRENCY=5

-- The frontend uses:
VITE_API_BASE_URL=http://localhost:8000
