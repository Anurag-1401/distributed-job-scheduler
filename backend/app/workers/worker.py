from app.websocket import publish_job_update
import asyncio
import logging
import uuid
from datetime import datetime, timezone

from sqlalchemy import select

from app.core.config import get_settings
from app.db import get_session_factory
from app.models import (
    Job,
    JobExecution,
    Worker,
    WorkerHeartbeat,
    WorkerStatus,
)
from app.services.jobs import (
    claim_job,
    finish_execution,
    recover_abandoned_jobs,
    start_execution,
)
from app.tasks import execute_task

logger = logging.getLogger(__name__)


class WorkerProcess:

    def __init__(
        self,
        worker_key: str | None = None,
    ) -> None:

        settings = get_settings()

        self.worker_key = (
            worker_key
            or settings.worker_id
            or f"worker-{uuid.uuid4()}"
        )

        self.max_concurrency = settings.max_concurrency
        self.poll_interval = settings.poll_interval_seconds
        self.heartbeat_interval = (
            settings.heartbeat_interval_seconds
        )
        self.lease_timeout = (
            settings.lease_timeout_seconds
        )

        self.stop_event = asyncio.Event()

        self.worker_id: uuid.UUID | None = None

        self.tasks: set[asyncio.Task] = set()

    # ---------------------------------------------------------
    # REGISTER
    # ---------------------------------------------------------

    async def register(self) -> None:

        async with get_session_factory()() as session:

            worker = await session.scalar(
                select(Worker).where(
                    Worker.worker_key == self.worker_key
                )
            )

            if worker is None:

                worker = Worker(
                    worker_key=self.worker_key,
                    max_concurrency=self.max_concurrency,
                )

                session.add(worker)
                await session.flush()

            worker.status = WorkerStatus.ONLINE
            worker.max_concurrency = self.max_concurrency
            worker.last_heartbeat_at = (
                datetime.now(timezone.utc)
            )

            await session.commit()

            self.worker_id = worker.id

            logger.info(
                "WORKER REGISTERED | worker=%s | id=%s | max=%s",
                self.worker_key,
                worker.id,
                worker.max_concurrency,
            )

    # ---------------------------------------------------------
    # HEARTBEAT
    # ---------------------------------------------------------

    async def heartbeat_loop(self) -> None:

        while not self.stop_event.is_set():

            try:
                await asyncio.wait_for(
                    self.stop_event.wait(),
                    timeout=self.heartbeat_interval,
                )
                break

            except asyncio.TimeoutError:
                pass

            if self.worker_id is None:
                continue

            async with get_session_factory()() as session:

                worker = await session.get(
                    Worker,
                    self.worker_id,
                )

                if worker:

                    worker.last_heartbeat_at = (
                        datetime.now(timezone.utc)
                    )

                    worker.current_job_count = len(
                        self.tasks
                    )

                    session.add(
                        WorkerHeartbeat(
                            worker_id=worker.id,
                            status=worker.status,
                            current_job_count=len(
                                self.tasks
                            ),
                        )
                    )

                    await session.commit()

    # ---------------------------------------------------------
    # EXECUTE JOB
    # ---------------------------------------------------------

    async def execute_claimed(
        self,
        job_id: uuid.UUID,
    ) -> None:

        execution_id = None

        logger.info(
            "EXECUTE START | worker=%s | job=%s",
            self.worker_key,
            job_id,
        )

        try:

            async with get_session_factory()() as session:

                job = await session.get(
                    Job,
                    job_id,
                )

                worker = await session.get(
                    Worker,
                    self.worker_id,
                )

                if job is None or worker is None:

                    logger.error(
                        "EXECUTE MISSING | job=%s",
                        job_id,
                    )

                    return

                await session.refresh(
                    job,
                    attribute_names=["queue"],
                )

                await session.refresh(
                    job.queue,
                    attribute_names=["retry_policy"],
                )

                execution = await start_execution(
                    session,
                    job,
                    worker,
                )

                await session.commit()

                await publish_job_update(
                    job,
                    event="job.updated",
                )

                execution_id = execution.id

            # -------------------------------------------------
            # TASK
            # -------------------------------------------------

            logger.info(
                "TASK START | job=%s | type=%s",
                job_id,
                job.task_type,
            )

            task_payload = dict(job.payload or {})
            task_payload["_attempt"] = getattr(job, "attempt", 1)

            result = await execute_task(
                job.task_type,
                task_payload,
            )

            logger.info(
                "TASK SUCCESS | job=%s",
                job_id,
            )

            # -------------------------------------------------
            # FINISH
            # -------------------------------------------------

            async with get_session_factory()() as session:

                job = await session.get(
                    Job,
                    job_id,
                )

                worker = await session.get(
                    Worker,
                    self.worker_id,
                )

                execution = await session.get(
                    JobExecution,
                    execution_id,
                )

                if job and worker and execution:

                    await session.refresh(
                        job,
                        attribute_names=["queue"],
                    )

                    await session.refresh(
                        job.queue,
                        attribute_names=[
                            "retry_policy"
                        ],
                    )

                    await finish_execution(
                        session,
                        job,
                        execution,
                        True,
                        result=result,
                    )

                    worker.current_job_count = max(
                        0,
                        worker.current_job_count - 1,
                    )

                    await session.commit()

                    await publish_job_update(
    job,
    event="job.updated",
)

                    logger.info(
                        "EXECUTE COMPLETE | job=%s | worker=%s",
                        job_id,
                        self.worker_key,
                    )

        except asyncio.CancelledError:
            raise

        except Exception as exc:

            logger.exception(
                "JOB EXECUTION FAILED | job=%s | worker=%s",
                job_id,
                self.worker_key,
            )

            if execution_id:

                async with get_session_factory()() as session:

                    job = await session.get(
                        Job,
                        job_id,
                    )

                    worker = await session.get(
                        Worker,
                        self.worker_id,
                    )

                    execution = await session.get(
                        JobExecution,
                        execution_id,
                    )

                    if job and worker and execution:

                        await session.refresh(
                            job,
                            attribute_names=["queue"],
                        )

                        await session.refresh(
                            job.queue,
                            attribute_names=[
                                "retry_policy"
                            ],
                        )

                        await finish_execution(
                            session,
                            job,
                            execution,
                            False,
                            error=str(exc),
                        )

                        worker.current_job_count = max(
                            0,
                            worker.current_job_count - 1,
                        )

                        await session.commit()

                        await publish_job_update(
    job,
    event="job.updated",
)

    # ---------------------------------------------------------
    # POLL
    # ---------------------------------------------------------

    async def poll_loop(self) -> None:

        while not self.stop_event.is_set():

            job = None

            if (
                self.worker_id is not None
                and len(self.tasks)
                < self.max_concurrency
            ):

                async with get_session_factory()() as session:

                    worker = await session.get(
                        Worker,
                        self.worker_id,
                    )

                    if worker:

                        job = await claim_job(
                            session,
                            worker,
                        )

                        await session.commit()

                if job:

                    logger.info(
                        "JOB CLAIMED BY POLLER | worker=%s | job=%s",
                        self.worker_key,
                        job.id,
                    )

                    task = asyncio.create_task(
                        self.execute_claimed(
                            job.id
                        ),
                        name=f"job-{job.id}",
                    )

                    self.tasks.add(task)

                    task.add_done_callback(
                        self.tasks.discard
                    )

            if not job:

                try:

                    await asyncio.wait_for(
                        self.stop_event.wait(),
                        timeout=self.poll_interval,
                    )

                except asyncio.TimeoutError:
                    pass

    # ---------------------------------------------------------
    # RECOVERY
    # ---------------------------------------------------------

    async def recovery_loop(self) -> None:

        interval = max(
            5.0,
            self.lease_timeout / 2,
        )

        while not self.stop_event.is_set():

            async with get_session_factory()() as session:

                recovered = await recover_abandoned_jobs(
                    session,
                    self.lease_timeout,
                )

                await session.commit()

                if recovered:

                    logger.warning(
                        "RECOVERED JOBS | count=%s",
                        recovered,
                    )

            try:

                await asyncio.wait_for(
                    self.stop_event.wait(),
                    timeout=interval,
                )

            except asyncio.TimeoutError:
                pass

    # ---------------------------------------------------------
    # RUN
    # ---------------------------------------------------------

    async def run_registered(self) -> None:

        logger.info(
            "WORKER LOOP RUNNING | worker=%s | id=%s",
            self.worker_key,
            self.worker_id,
        )

        if self.worker_id is None:
            await self.register()

        await asyncio.gather(
            self.heartbeat_loop(),
            self.poll_loop(),
            self.recovery_loop(),
        )

    # ---------------------------------------------------------
    # STOP
    # ---------------------------------------------------------

    async def stop(self) -> None:

        self.stop_event.set()

        if self.worker_id:

            if self.tasks:

                await asyncio.gather(
                    *list(self.tasks),
                    return_exceptions=True,
                )

            async with get_session_factory()() as session:

                worker = await session.get(
                    Worker,
                    self.worker_id,
                )

                if worker:

                    worker.current_job_count = 0
                    worker.status = WorkerStatus.OFFLINE
                    worker.last_heartbeat_at = (
                        datetime.now(timezone.utc)
                    )

                    await session.commit()


async def main() -> None:

    process = WorkerProcess()

    await process.register()

    await process.run_registered()