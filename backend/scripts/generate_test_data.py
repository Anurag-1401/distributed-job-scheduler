#!/usr/bin/env python3
"""Generate a comprehensive integration/demo dataset for the Distributed Job Scheduler.

Run from the backend directory:
    python scripts/generate_test_data.py --email your@email.com --password 'your-password'

If --email/--password are omitted, a fresh test user is registered automatically and
its credentials are printed. The script intentionally uses the public HTTP API so the
real auth -> organization -> project -> queue -> job -> worker pipeline is exercised.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import random
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import httpx


DEFAULT_BASE_URL = os.getenv("SCHEDULER_BASE_URL", "http://localhost:8000")


class ApiError(RuntimeError):
    pass

def validate_priority(
    value: Any,
    *,
    kind: str,
    name: str = "",
) -> int:
    """Validate scheduler priority.

    Rules:
    - priority must be an integer
    - priority must be positive
    - lower number means higher priority
    - 1 is the highest priority
    """
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ApiError(
            f"Invalid {kind} priority for {name}: {value!r}"
        ) from exc

    if number <= 0:
        raise ApiError(
            f"Invalid {kind} priority for {name}: {number}. "
            "Priority must be a positive integer; "
            "lower number = higher priority."
        )

    return number


class SchedulerApi:
    def __init__(self, base_url: str, client: httpx.AsyncClient) -> None:
        self.base_url = base_url.rstrip("/")
        self.client = client
        self.token: str | None = None

    async def request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
        expected: set[int] = {200, 201, 204},
    ) -> Any:
        merged = dict(headers or {})
        if self.token:
            merged["Authorization"] = f"Bearer {self.token}"

        response = await self.client.request(
            method,
            f"{self.base_url}{path}",
            json=json_body,
            headers=merged,
        )

        if response.status_code not in expected:
            try:
                detail = response.json()
            except Exception:
                detail = response.text
            raise ApiError(f"{method} {path} -> {response.status_code}: {detail}")

        if response.status_code == 204 or not response.content:
            return None
        return response.json()

    async def register_or_login(self, email: str, password: str, full_name: str) -> dict[str, Any]:
        try:
            data = await self.request(
                "POST",
                "/api/v1/auth/register",
                json_body={"email": email, "password": password, "full_name": full_name},
                expected={201},
            )
        except ApiError as exc:
            if "409" not in str(exc):
                raise
            data = await self.request(
                "POST",
                "/api/v1/auth/login",
                json_body={"email": email, "password": password},
                expected={200},
            )
        self.token = data["access_token"]
        return data["user"]


async def create_job(
    api: SchedulerApi,
    queue_id: str,
    *,
    task_type: str = "echo",
    payload: dict[str, Any] | None = None,
    priority: int = 10,
    job_type: str = "IMMEDIATE",
    delay_seconds: float | None = None,
    scheduled_at: datetime | None = None,
    cron_expression: str | None = None,
    timezone_name: str = "UTC",
    idempotency_key: str | None = None,
) -> dict[str, Any]:
    body: dict[str, Any] = {
        "queue_id": queue_id,
        "task_type": task_type,
        "type": job_type,
        "payload": payload or {},
        "priority": priority,
    }
    if delay_seconds is not None:
        body["delay_seconds"] = delay_seconds
    if scheduled_at is not None:
        body["scheduled_at"] = scheduled_at.isoformat()
    if cron_expression is not None:
        body["cron_expression"] = cron_expression
        body["timezone"] = timezone_name
    if idempotency_key is not None:
        body["idempotency_key"] = idempotency_key
    return await api.request("POST", "/api/v1/jobs", json_body=body, expected={201})


async def main() -> int:
    parser = argparse.ArgumentParser(description="Generate comprehensive scheduler test data")
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--email", default=os.getenv("TEST_EMAIL"))
    parser.add_argument("--password", default=os.getenv("TEST_PASSWORD"))
    parser.add_argument("--full-name", default="Scheduler Integration Tester")
    parser.add_argument("--seed", type=int, default=20260823)
    parser.add_argument("--immediate-count", type=int, default=20)
    parser.add_argument("--sleep-count", type=int, default=8)
    parser.add_argument("--batch-count", type=int, default=10)
    args = parser.parse_args()

    random.seed(args.seed)

    if not args.email:
        suffix = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        args.email = f"scheduler-test-{suffix}@example.com"
    if not args.password:
        args.password = "SchedulerTest123!"

    manifest: dict[str, Any] = {
        "created_at": datetime.now(timezone.utc).isoformat(),
        "base_url": args.base_url,
        "seed": args.seed,
        "priority_rule": "positive integer only; lower number means higher priority; 1 is highest",
        "user": {"email": args.email, "password": args.password},
        "organizations": [],
        "projects": [],
        "queues": [],
        "jobs": [],
        "batch_parent": None,
        "cancelled_job": None,
        "idempotency_pair": [],
    }

    timeout = httpx.Timeout(30.0, connect=10.0)
    async with httpx.AsyncClient(timeout=timeout) as client:
        api = SchedulerApi(args.base_url, client)

        print("[1/8] Authenticating test user...")
        user = await api.register_or_login(args.email, args.password, args.full_name)
        print(f"      user={user['email']} id={user['id']}")

        print("[2/8] Creating organization...")
        org_slug = f"scheduler-test-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"
        org = await api.request(
            "POST",
            "/api/v1/organizations",
            json_body={"name": "Scheduler Integration Test Org", "slug": org_slug},
            expected={201},
        )
        manifest["organizations"].append(org)
        org_id = org["id"]
        print(f"      organization={org_id}")

        print("[3/8] Creating 3 projects...")
        project_specs = [
            ("Immediate & Priority Tests", "immediate-priority-tests"),
            ("Scheduling & Delay Tests", "scheduling-delay-tests"),
            ("Reliability & Concurrency Tests", "reliability-concurrency-tests"),
        ]
        projects: list[dict[str, Any]] = []
        for name, slug in project_specs:
            project = await api.request(
                "POST",
                "/api/v1/projects",
                json_body={"organization_id": org_id, "name": name, "slug": slug},
                expected={201},
            )
            projects.append(project)
            manifest["projects"].append(project)
        print(f"      projects={len(projects)}")

        print("[4/8] Creating queues with different priority/concurrency/retry policies...")
        queue_specs = [
            # Project 0
            (
                0,
                "high-priority",
                1,
                5,
                {
                    "max_attempts": 3,
                    "base_delay_seconds": 2,
                    "max_delay_seconds": 10,
                    "jitter": False,
                    "strategy": "FIXED",
                },
            ),
            (
                0,
                "normal-priority",
                10,
                5,
                {
                    "max_attempts": 3,
                    "base_delay_seconds": 2,
                    "max_delay_seconds": 10,
                    "jitter": False,
                    "strategy": "LINEAR",
                },
            ),

            # Project 1
            (
                1,
                "scheduled-jobs",
                20,
                5,
                {
                    "max_attempts": 3,
                    "base_delay_seconds": 2,
                    "max_delay_seconds": 10,
                    "jitter": False,
                    "strategy": "EXPONENTIAL",
                },
            ),
            (
                1,
                "delayed-jobs",
                10,
                5,
                {
                    "max_attempts": 3,
                    "base_delay_seconds": 2,
                    "max_delay_seconds": 10,
                    "jitter": False,
                    "strategy": "FIXED",
                },
            ),

            # Project 2
            (
                2,
                "single-concurrency",
                50,
                1,
                {
                    "max_attempts": 3,
                    "base_delay_seconds": 2,
                    "max_delay_seconds": 10,
                    "jitter": False,
                    "strategy": "FIXED",
                },
            ),
            (
                2,
                "reliability",
                30,
                10,
                {
                    "max_attempts": 3,
                    "base_delay_seconds": 2,
                    "max_delay_seconds": 10,
                    "jitter": False,
                    "strategy": "EXPONENTIAL",
                },
            ),
        ]

        queues: list[dict[str, Any]] = []
        for project_index, name, priority, concurrency, retry_policy in queue_specs:
            queue = await api.request(
                "POST",
                "/api/v1/queues",
                json_body={
                    "project_id": projects[project_index]["id"],
                    "name": name,
                    "priority": priority,
                    "concurrency_limit": concurrency,
                    "retry_policy": retry_policy,
                },
                expected={201},
            )
            validate_priority(queue["priority"], kind="queue", name=name)
            queues.append(queue)
            manifest["queues"].append(queue)
        print(f"      queues={len(queues)}")

        high_q = queues[0]["id"]
        normal_q = queues[1]["id"]
        scheduled_q = queues[2]["id"]
        delayed_q = queues[3]["id"]
        single_q = queues[4]["id"]
        reliability_q = queues[5]["id"]

        def record(category: str, job: dict[str, Any]) -> None:
            validate_priority(job["priority"], kind="job", name=str(job["id"]))
            manifest["jobs"].append({
                "category": category,
                "id": job["id"],
                "queue_id": job["queue_id"],
                "type": job["job_type"],
                "priority": job["priority"],
                "state_at_creation": job["state"],
            })

        print("[5/8] Creating immediate jobs with same and different priorities...")
        for i in range(args.immediate_count):
            if i < 8:
                priority = 10  # deliberately identical priority group
                category = "immediate_same_priority"
            else:
                priority = [1, 2, 3, 5, 10, 20, 50][(i - 8) % 7]
                category = "immediate_mixed_priority"
            queue_id = high_q if i % 2 == 0 else normal_q
            job = await create_job(
                api,
                queue_id,
                payload={"scenario": category, "sequence": i, "seed": args.seed},
                priority=priority,
            )
            record(category, job)

        print("[6/8] Creating delayed/scheduled/cron jobs...")
        now = datetime.now(timezone.utc)

        for i, delay in enumerate([10, 15, 20, 25, 30]):
            job = await create_job(
                api,
                delayed_q,
                task_type="echo",
                payload={"scenario": "delayed", "delay_seconds": delay, "sequence": i},
                priority=20,
                job_type="DELAYED",
                delay_seconds=delay,
            )
            record("delayed", job)

        for i, seconds in enumerate([15, 20, 30, 40, 50]):
            run_at = now + timedelta(seconds=seconds)
            job = await create_job(
                api,
                scheduled_q,
                payload={"scenario": "scheduled", "scheduled_offset_seconds": seconds, "sequence": i},
                priority=30,
                job_type="SCHEDULED",
                scheduled_at=run_at,
            )
            record("scheduled", job)

        for i in range(2):
            job = await create_job(
                api,
                scheduled_q,
                payload={"scenario": "cron", "sequence": i},
                priority=15,
                job_type="CRON",
                cron_expression="*/1 * * * *",
                timezone_name="UTC",
            )
            record("cron_template", job)

        print("[7/8] Creating concurrency, retry, DLQ, flaky, batch, cancel and idempotency tests...")
        # Single-concurrency queue: long-running jobs should execute one at a time.
        for i in range(args.sleep_count):
            job = await create_job(
                api,
                single_q,
                task_type="sleep",
                payload={"seconds": 3, "scenario": "queue_concurrency", "sequence": i},
                priority=40,
            )
            record("queue_concurrency_sleep", job)

        # One flaky job should fail once and then succeed because the worker injects _attempt.
        flaky = await create_job(
            api,
            reliability_q,
            task_type="flaky_task",
            payload={"fail_until_attempt": 1, "scenario": "retry_then_success"},
            priority=60,
        )
        record("retry_then_success", flaky)

        # One permanent failure should eventually exhaust retries and enter DLQ.
        dlq_job = await create_job(
            api,
            reliability_q,
            task_type="failure_simulation",
            payload={"message": "Intentional permanent failure for DLQ test", "scenario": "dead_letter"},
            priority=55,
        )
        record("dead_letter", dlq_job)

        # Idempotency: the second request should return the same job ID.
        idem_key = f"scheduler-idempotency-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}"
        idem1 = await create_job(
            api,
            normal_q,
            payload={"scenario": "idempotency", "request": 1},
            priority=5,
            idempotency_key=idem_key,
        )
        idem2 = await create_job(
            api,
            normal_q,
            payload={"scenario": "idempotency", "request": 2},
            priority=5,
            idempotency_key=idem_key,
        )
        manifest["idempotency_pair"] = [idem1["id"], idem2["id"]]
        record("idempotency_first", idem1)
        record("idempotency_second_same_job", idem2)

        # Batch test: parent is cancelled by the API, children are executable.
        batch_items = [
            {"task_type": "echo", "payload": {"scenario": "batch", "sequence": i}, "priority": (i % 3) + 1}
            for i in range(args.batch_count)
        ]
        batch = await api.request(
            "POST",
            "/api/v1/jobs/batch",
            json_body={
                "queue_id": normal_q,
                "priority": 10,
                "jobs": batch_items,
            },
            expected={201},
        )
        manifest["batch_parent"] = batch["id"]
        record("batch_parent_cancelled", batch)

        # Cancellation test: create a future delayed job and cancel it immediately.
        cancellable = await create_job(
            api,
            delayed_q,
            task_type="sleep",
            payload={"seconds": 5, "scenario": "cancellation"},
            priority=1,
            job_type="DELAYED",
            delay_seconds=60,
        )
        await api.request("POST", f"/api/v1/jobs/{cancellable['id']}/cancel", expected={200})
        manifest["cancelled_job"] = cancellable["id"]
        record("cancelled", cancellable)

        # A few data-processing and email simulation tasks exercise other registered handlers.
        for i in range(5):
            task_type = "data_processing" if i % 2 == 0 else "email_simulation"
            payload = (
                {"scenario": "data_processing", "values": list(range(i + 1))}
                if task_type == "data_processing"
                else {"scenario": "email_simulation", "recipient": f"test-{i}@example.com"}
            )
            job = await create_job(api, normal_q, task_type=task_type, payload=payload, priority=3)
            record(task_type, job)

        print("[8/8] Writing manifest...")
        output_dir = Path(__file__).resolve().parent
        output_dir.mkdir(parents=True, exist_ok=True)
        manifest_path = output_dir / f"test_run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        manifest_path.write_text(json.dumps(manifest, indent=2, default=str), encoding="utf-8")

        counts: dict[str, int] = {}
        for item in manifest["jobs"]:
            category = item["category"]
            counts[category] = counts.get(category, 0) + 1

        print("\n========== TEST DATA CREATED ==========")
        print(f"Base URL          : {args.base_url}")
        print(f"Test user         : {args.email}")
        print(f"Password          : {args.password}")
        print(f"Organization      : {org_id}")
        print(f"Projects          : {len(manifest['projects'])}")
        print(f"Queues            : {len(manifest['queues'])}")
        print(f"Job records       : {len(manifest['jobs'])}")
        print(f"Batch parent      : {manifest['batch_parent']}")
        print(f"Cancelled job     : {manifest['cancelled_job']}")
        print(f"Idempotency IDs   : {manifest['idempotency_pair']}")
        print("Priority rule     : POSITIVE ONLY; LOWER NUMBER = HIGHER PRIORITY")
        print("Highest priority  : 1")
        print("\nJob categories:")
        for key in sorted(counts):
            print(f"  {key:32s} {counts[key]:>3}")

        print("\n========== EXECUTION TEST SUMMARY ==========")
        print("Immediate         : same-priority + mixed-priority")
        print("Delayed           : 10/15/20/25/30 second delays")
        print("Scheduled         : 15/20/30/40/50 second schedules")
        print("CRON              : 2 recurring templates")
        print("Concurrency       : 8 jobs on a queue limited to 1")
        print("Retry             : flaky job (fail once, then succeed)")
        print("DLQ               : permanent failure until retry exhaustion")
        print("Idempotency       : same key submitted twice")
        print("Batch             : parent + child jobs")
        print("Cancellation      : future delayed job cancelled immediately")
        print("Task handlers     : echo + sleep + data_processing + email_simulation")
        print(f"\nManifest          : {manifest_path}")
        print("=============================================")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(asyncio.run(main()))
    except KeyboardInterrupt:
        raise SystemExit(130)