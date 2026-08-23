# Database

Alembic owns schema changes. Production startup does not create tables automatically. Run the initial migration before starting services.

The normalized tables are `users`, `organizations`, `organization_members`, `projects`, `queues`, `retry_policies`, `jobs`, `job_executions`, `job_logs`, `workers`, `worker_heartbeats`, `scheduled_jobs`, and `dead_letter_jobs`.

The job claim index supports queue/state/availability/priority polling. UUIDs are used for identifiers, timestamps are timezone-aware, and organization membership is the access boundary.

## PostgreSQL vs Redis responsibilities

PostgreSQL is the source of truth for all persistent state. Redis is supporting infrastructure for coordination, caching, and rate limiting. No job state is ever solely in Redis.
