# Worker design

A worker registers a durable identity, sends heartbeat rows, polls active queues, atomically claims jobs, and runs registered task handlers concurrently. Queue-level concurrency is checked against active claimed/running jobs before each claim. Shutdown marks the worker offline; stale claims are requeued by the recovery loop after the lease timeout.

Task payloads select a named handler (`echo`, `http_request`, `sleep`, `email_simulation`, or `data_processing`). Arbitrary Python from payloads is never executed.

## Worker failure recovery

Workers whose heartbeat expires are considered offline. The recovery loop identifies jobs in CLAIMED or RUNNING state whose `claimed_at` is older than the lease timeout, and requeues them for processing. This provides at-least-once execution semantics — a crashed worker's job may execute again.
