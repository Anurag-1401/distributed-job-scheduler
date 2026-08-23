# Job lifecycle

```mermaid
stateDiagram-v2
    [*] --> SCHEDULED
    SCHEDULED --> QUEUED: due
    QUEUED --> CLAIMED: row lock + worker assignment
    RETRYING --> CLAIMED: backoff elapsed
    CLAIMED --> RUNNING: execution record
    RUNNING --> COMPLETED: success
    RUNNING --> RETRYING: failure and attempts remain
    RUNNING --> DEAD_LETTER: retry exhaustion
    CLAIMED --> RETRYING: lease recovery
```

The database is authoritative. Claiming uses a transaction and `FOR UPDATE SKIP LOCKED`, so competing workers cannot claim the same row. Execution is at-least-once: a worker crash can cause a previously started task to run again after lease recovery. Exactly-once execution is not claimed.
