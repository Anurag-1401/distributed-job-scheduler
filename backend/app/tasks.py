import asyncio
from collections.abc import Awaitable, Callable

import httpx

TaskHandler = Callable[[dict], Awaitable[dict]]


async def echo(payload: dict) -> dict:
    return payload


async def sleep_task(payload: dict) -> dict:
    seconds = min(float(payload.get("seconds", 0)), 300)
    await asyncio.sleep(seconds)
    return {"slept_seconds": seconds}


async def email_simulation(payload: dict) -> dict:
    return {"simulated": True, "recipient": payload.get("recipient")}


async def data_processing(payload: dict) -> dict:
    values = payload.get("values", [])
    return {
        "count": len(values),
        "sum": sum(v for v in values if isinstance(v, (int, float))),
    }


async def http_request(payload: dict) -> dict:
    url = payload.get("url")
    if not isinstance(url, str) or not url.startswith(("https://", "http://")):
        raise ValueError("payload.url must be an HTTP(S) URL")
    async with httpx.AsyncClient(timeout=10, follow_redirects=False) as client:
        response = await client.request(payload.get("method", "GET"), url)
    return {"status_code": response.status_code, "body": response.text[:10000]}


TASKS: dict[str, TaskHandler] = {
    "echo": echo,
    "sleep": sleep_task,
    "email_simulation": email_simulation,
    "data_processing": data_processing,
    "http_request": http_request,
}


async def execute_task(task_type: str, payload: dict) -> dict:
    handler = TASKS.get(task_type)
    if handler is None:
        raise ValueError(f"Unsupported task type: {task_type}")
    return await handler(payload)
