import asyncio
import logging
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from croniter import croniter
from redis.asyncio import Redis
from sqlalchemy import select

from app.core.config import get_settings
from app.db import get_session_factory
from app.models import (
    Job,
    JobState,
    JobType,
    ScheduledJob,
)
from app.workers.worker import WorkerProcess

logger = logging.getLogger(__name__)


class SchedulerService:

    def __init__(self, redis: Redis) -> None:

        self.redis = redis
        self.stop_event = asyncio.Event()

        settings = get_settings()

        self.interval = (
            settings.scheduler_interval_seconds
        )

        self.lock_ttl = (
            settings.scheduler_lock_ttl_seconds
        )

    async def tick(self) -> None:

        lock_key = (
            "distributed-job-scheduler:scheduler-leader"
        )

        acquired = await self.redis.set(
            lock_key,
            str(uuid.uuid4()),
            nx=True,
            ex=self.lock_ttl,
        )

        if not acquired:
            return

        now = datetime.now(timezone.utc)

        async with get_session_factory()() as session:

            # -------------------------------------------------
            # Scheduled jobs
            # -------------------------------------------------

            due = list(
                (
                    await session.scalars(
                        select(Job)
                        .where(
                            Job.state == JobState.SCHEDULED,
                            Job.available_at <= now,
                            Job.is_schedule_template.is_(
                                False
                            ),
                        )
                    )
                ).all()
            )

            for job in due:

                job.state = JobState.QUEUED

            # -------------------------------------------------
            # Recurring jobs
            # -------------------------------------------------

            recurring = list(
                (
                    await session.scalars(
                        select(ScheduledJob)
                        .where(
                            ScheduledJob.enabled,
                            ScheduledJob.next_run_at <= now,
                        )
                    )
                ).all()
            )

            for schedule in recurring:

                template = await session.get(
                    Job,
                    schedule.job_template_id,
                )

                if not template:

                    schedule.enabled = False
                    continue

                try:
                    tz = ZoneInfo(
                        schedule.timezone
                    )
                except Exception:
                    tz = ZoneInfo("UTC")

                local_now = now.astimezone(tz)

                next_local = croniter(
                    schedule.cron_expression,
                    local_now,
                ).get_next(datetime)

                next_run = (
                    next_local
                    .replace(tzinfo=tz)
                    .astimezone(timezone.utc)
                )

                child = Job(
                    queue_id=template.queue_id,
                    task_type=template.task_type,
                    job_type=JobType.CRON,
                    payload=template.payload,
                    priority=template.priority,
                    state=JobState.QUEUED,
                    available_at=now,
                    scheduled_at=now,
                )

                session.add(child)

                schedule.last_run_at = now
                schedule.next_run_at = next_run

            await session.commit()

    async def run(self) -> None:

        logger.info(
            "SCHEDULER LOOP RUNNING | interval=%ss",
            self.interval,
        )

        while not self.stop_event.is_set():

            try:

                await self.tick()

                logger.debug(
                    "SCHEDULER TICK COMPLETED"
                )

            except asyncio.CancelledError:
                raise

            except Exception:

                logger.exception(
                    "SCHEDULER ITERATION FAILED"
                )

            try:

                await asyncio.wait_for(
                    self.stop_event.wait(),
                    timeout=self.interval,
                )

            except asyncio.TimeoutError:
                pass

    def stop(self) -> None:
        self.stop_event.set()


class UnifiedRuntime:

    def __init__(self) -> None:

        settings = get_settings()

        self.redis = Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )

        self.scheduler = SchedulerService(
            self.redis
        )

        self.workers = [
            WorkerProcess(
                worker_key=(
                    settings.worker_id
                    or "app-worker"
                )
                + f"-{i + 1}"
            )
            for i in range(
                max(
                    1,
                    settings.worker_count,
                )
            )
        ]

        self.tasks: list[asyncio.Task] = []

    async def start(self) -> None:

        await self.redis.ping()

        await asyncio.gather(
            *(
                worker.register()
                for worker in self.workers
            )
        )

        scheduler_task = asyncio.create_task(
            self.scheduler.run(),
            name="scheduler",
        )

        self.tasks = [
            scheduler_task
        ]

        logger.info(
            "SCHEDULER STARTED"
        )

        for worker in self.workers:

            task = asyncio.create_task(
                worker.run_registered(),
                name=worker.worker_key,
            )

            self.tasks.append(task)

            logger.info(
                "WORKER STARTED | worker=%s",
                worker.worker_key,
            )

        logger.info(
            "UNIFIED RUNTIME STARTED | workers=%s",
            len(self.workers),
        )

    async def stop(self) -> None:

        self.scheduler.stop()

        await asyncio.gather(
            *(
                worker.stop()
                for worker in self.workers
            ),
            return_exceptions=True,
        )

        for task in self.tasks:
            task.cancel()

        if self.tasks:

            await asyncio.gather(
                *self.tasks,
                return_exceptions=True,
            )

        await self.redis.aclose()

        logger.info(
            "UNIFIED RUNTIME STOPPED"
        )


runtime = UnifiedRuntime()