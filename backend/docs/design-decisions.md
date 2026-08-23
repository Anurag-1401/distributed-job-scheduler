# Design decisions

- PostgreSQL owns durable state and locking; Redis is supporting infrastructure rather than a second queue of record.
- `FOR UPDATE SKIP LOCKED` provides safe multi-worker claiming without a global mutable coordinator.
- Worker leases and heartbeat freshness allow recovery after process failure, with at-least-once semantics.
- Organization membership is enforced in every resource query to prevent cross-organization access.
- Idempotency keys are unique per queue and return the original job for repeated creation requests.
- The scheduler locks due rows and advances recurring schedules in the same transaction to avoid duplicate generation when multiple schedulers run.
- Alembic is used for schema evolution; automatic production table creation is intentionally avoided.

## Idempotency

Job creation supports an optional `idempotency_key` unique per queue. Submitting the same key twice returns the original job instead of creating a duplicate. This prevents accidental duplication from retries or network issues.

## At-least-once vs exactly-once

This system provides at-least-once execution. A worker crash after a job starts may cause the job to run again after lease recovery. Exactly-once is not guaranteed. Design external side effects (emails, payments, API calls) to be idempotent.
