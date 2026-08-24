import asyncio
from collections.abc import Awaitable, Callable

import httpx


TaskHandler = Callable[[dict], Awaitable[dict]]


async def echo(payload: dict) -> dict:
    return payload


async def sleep_task(payload: dict) -> dict:
    seconds = min(float(payload.get("seconds", 0)), 300)
    await asyncio.sleep(seconds)

    return {
        "slept_seconds": seconds,
    }


async def email_simulation(payload: dict) -> dict:
    return {
        "simulated": True,
        "recipient": payload.get("recipient"),
    }


async def data_processing(payload: dict) -> dict:
    values = payload.get("values", [])

    return {
        "count": len(values),
        "sum": sum(
            v
            for v in values
            if isinstance(v, (int, float))
        ),
    }


async def http_request(payload: dict) -> dict:
    url = payload.get("url")

    if not isinstance(url, str) or not url.startswith(
        ("https://", "http://")
    ):
        raise ValueError(
            "payload.url must be an HTTP(S) URL"
        )

    async with httpx.AsyncClient(
        timeout=10,
        follow_redirects=False,
    ) as client:
        response = await client.request(
            payload.get("method", "GET"),
            url,
        )

    return {
        "status_code": response.status_code,
        "body": response.text[:10000],
    }


# ---------------------------------------------------------------------------
# TEST / RELIABILITY TASKS
# ---------------------------------------------------------------------------

async def flaky_task(payload: dict) -> dict:
    """
    Test task used to verify retry-then-success behavior.

    Example payload:
        {
            "fail_until_attempt": 1
        }

    Attempt 1 -> FAIL
    Attempt 2 -> SUCCESS

    If fail_until_attempt is 2:

    Attempt 1 -> FAIL
    Attempt 2 -> FAIL
    Attempt 3 -> SUCCESS

    The worker must provide the current attempt in payload["_attempt"].
    """

    fail_until_attempt = int(
        payload.get("fail_until_attempt", 1)
    )

    attempt = int(
        payload.get("_attempt", 1)
    )

    if fail_until_attempt < 0:
        fail_until_attempt = 0

    if attempt <= fail_until_attempt:
        raise RuntimeError(
            f"Intentional flaky failure: "
            f"attempt={attempt}, "
            f"fail_until_attempt={fail_until_attempt}"
        )

    return {
        "status": "success",
        "task": "flaky_task",
        "attempt": attempt,
        "fail_until_attempt": fail_until_attempt,
        "message": "Flaky task succeeded after retry",
    }


async def failure_simulation(payload: dict) -> dict:
    """
    Test task used to verify permanent failure and DLQ behavior.

    This task ALWAYS fails intentionally.

    The scheduler should:
        attempt 1 -> FAIL
        retry
        attempt 2 -> FAIL
        retry
        attempt 3 -> FAIL
        max attempts reached
        -> DEAD LETTER
    """

    message = payload.get(
        "message",
        "Intentional permanent failure for DLQ testing",
    )

    raise RuntimeError(message)


# ---------------------------------------------------------------------------
# TASK REGISTRY
# ---------------------------------------------------------------------------

TASKS: dict[str, TaskHandler] = {
    "echo": echo,
    "sleep": sleep_task,
    "email_simulation": email_simulation,
    "data_processing": data_processing,
    "http_request": http_request,

    # Reliability / integration tests
    "flaky_task": flaky_task,
    "failure_simulation": failure_simulation,
}


# ---------------------------------------------------------------------------
# TASK EXECUTOR
# ---------------------------------------------------------------------------

async def execute_task(
    task_type: str,
    payload: dict,
) -> dict:
    handler = TASKS.get(task_type)

    if handler is None:
        raise ValueError(
            f"Unsupported task type: {task_type}"
        )

    return await handler(payload)