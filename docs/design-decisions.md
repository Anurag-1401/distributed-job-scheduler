# Design decisions and risks

## Decisions

1. **PostgreSQL owns job state.** Redis is optional for rate limits and caches. Correctness does not depend on Redis.
2. **Claiming:** `SELECT … FOR UPDATE SKIP LOCKED` plus a **per-queue runtime row** so concurrency limits are exact under contention.
3. **At-least-once execution** with leases + heartbeats. No exactly-once claim.
4. **Idempotency keys** unique per queue on create (`UNIQUE (queue_id, idempotency_key)`). Same key + same payload returns the existing job; conflicting payload returns `409 IDEMPOTENCY_CONFLICT`.
5. **Task registry only.** Payloads cannot supply code.
6. **Argon2** for passwords; JWT access tokens (expiring). Refresh tokens deferred unless approved.
7. **RBAC** stored from day one (`OWNER/ADMIN/DEVELOPER/VIEWER`); enforce org isolation immediately; fine-grained permission matrix in services.
8. **Alembic only** — no metadata create_all in production.
9. **Page/limit pagination** first; cursors later if lists grow huge.
10. **Structured API errors** with stable `code` strings.
11. **Cron uniqueness** via `schedule_fires` unique constraint, not “check then insert”.
12. **Execution history is append-only.**

## Trade-offs

| Topic | Choice | Cost |
| --- | --- | --- |
| SKIP LOCKED | High throughput claims | Need integration tests under real Postgres |
| Queue counter row | Exact concurrency | Extra hotspot row per busy queue |
| Lease recovery | Safety vs stuck jobs | Possible duplicate run |
| Redis not for queues | Simpler truth | Cannot use Redis streams as primary |
| Polling workers | Simple ops | Idle latency = poll interval |

## Risks

- Queue runtime row can bottleneck a single hot queue (acceptable for v1; partition later).
- HTTP tasks can hammer third parties; need timeouts, size limits, SSRF policy (block link-local).
- Cron timezone bugs; default UTC.
- Heartbeat TTL vs long GC pauses → false recovery (tune lease ≫ heartbeat).
- Batch progress races; compute from jobs with indexes.

## Open questions (approval)

1. Confirm project path `C:\Users\Admin\Projects\scheduler-backend` and name `scheduler-backend`.
2. Argon2 vs bcrypt (recommendation: Argon2).
3. JWT access-only vs access+refresh.
4. DLQ manual retry: reset attempts or continue?
5. `RETRYING` as its own status vs `QUEUED` + `attempt_count`?
6. Recoverer inside scheduler process vs dedicated service?
7. SSRF allowlist for `http_request` tasks?
8. Multi-tenancy: one Postgres schema vs row-level org_id only (recommendation: org_id columns only)?
9. Should workers subscribe to all org queues or require explicit queue assignment?
10. Proceed to **phase 1 implementation** (Compose + models + Alembic + health) after you approve this plan?
