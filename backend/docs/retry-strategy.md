# Retry strategy

Policies support fixed, linear, and exponential backoff with a configurable maximum and bounded jitter. Attempts are recorded in `job_executions`. When attempts reach `max_attempts`, the job becomes `DEAD_LETTER` and a durable dead-letter record retains the final failure.

Retry schedules are approximate because jitter intentionally spreads load. Consumers should make task effects idempotent when possible.

## Examples

- Fixed: 10s, 10s, 10s
- Linear: 10s, 20s, 30s
- Exponential: 2s, 4s, 8s, 16s
