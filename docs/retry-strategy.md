# Retry strategy

Configured on `retry_policies` (queue default) and optional per-job override.

## Parameters

- `max_attempts` — total execution attempts including the first
- `base_delay_seconds`
- `max_delay_seconds`
- `strategy`: `FIXED` | `LINEAR` | `EXPONENTIAL`
- `jitter_ratio` — e.g. `0.1` → delay × uniform(0.9, 1.1)

Delay is applied **before the next attempt** by setting `run_after = now() + delay`. Status becomes `RETRYING` (claimable once due).

Let `n` be the attempt that just failed (`attempt_count` after increment). Next delay uses `n` as the retry index starting at 1.

| Strategy | Delay before next run |
| --- | --- |
| FIXED | `base` |
| LINEAR | `base * n` |
| EXPONENTIAL | `base * 2^(n-1)` |

All capped by `max_delay_seconds`, then jittered, minimum 0.

Examples:

- Fixed 10s: 10, 10, 10
- Linear 10s: 10, 20, 30
- Exponential 2s: 2, 4, 8, 16

Jitter reduces synchronized retry storms across many failed jobs.

## Exhaustion → DLQ

When `attempt_count >= max_attempts` after a failure:

1. Transition job `FAILED` → `DEAD_LETTER` (single transaction)
2. Insert `dead_letter_jobs` with reason, final error, attempts, worker, last execution
3. Job remains queryable; DLQ APIs list/inspect/retry/delete

DLQ retry: new `QUEUED` transition, reset or continue attempt budget (proposed default: **reset attempt_count to 0** on manual retry, record a `dlq_retry` event). Open for approval.

## Tests planned

- Each backoff formula (unit, freeze time)
- Exhaustion creates DLQ row and not another claim
- Jitter stays within bounds
