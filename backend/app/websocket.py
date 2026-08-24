from __future__ import annotations

import json
import logging

from typing import Any

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class JobWebSocketManager:
    def __init__(self) -> None:
        self.connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.add(websocket)

        logger.info(
            "WEBSOCKET CONNECTED | clients=%s",
            len(self.connections),
        )

    def disconnect(self, websocket: WebSocket) -> None:
        self.connections.discard(websocket)

        logger.info(
            "WEBSOCKET DISCONNECTED | clients=%s",
            len(self.connections),
        )

    async def broadcast(self, message: dict[str, Any]) -> None:
        if not self.connections:
            return

        data = json.dumps(message, default=str)

        disconnected: list[WebSocket] = []

        for websocket in self.connections:
            try:
                await websocket.send_text(data)
            except Exception:
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)

async def publish_job_update(
    job: Any,
    event: str = "job.updated",
) -> None:
    await job_ws_manager.broadcast(
        {
            "event": event,
            "job": {
                "id": str(job.id),
                "queue_id": str(job.queue_id),
                "task_type": job.task_type,
                "job_type": (
                    job.job_type.value
                    if hasattr(job.job_type, "value")
                    else str(job.job_type)
                ),
                "state": (
                    job.state.value
                    if hasattr(job.state, "value")
                    else str(job.state)
                ),
                "status": (
                    job.state.value
                    if hasattr(job.state, "value")
                    else str(job.state)
                ),
                "priority": job.priority,
                "attempts": job.attempts,
                "worker_id": (
                    str(job.worker_id)
                    if job.worker_id
                    else None
                ),
                "last_error": job.last_error,
                "scheduled_at": (
                    job.scheduled_at.isoformat()
                    if job.scheduled_at
                    else None
                ),
                "available_at": (
                    job.available_at.isoformat()
                    if job.available_at
                    else None
                ),
                "created_at": (
                    job.created_at.isoformat()
                    if job.created_at
                    else None
                ),
                "started_at": (
                    job.started_at.isoformat()
                    if job.started_at
                    else None
                ),
                "completed_at": (
                    job.completed_at.isoformat()
                    if job.completed_at
                    else None
                ),
            },
        }
    )


job_ws_manager = JobWebSocketManager()