import asyncio
import logging
from datetime import datetime, timezone

from croniter import croniter
from sqlalchemy import select

from app.db import get_session_factory
from app.models import Job, JobState, ScheduledJob

logger = logging.getLogger(__name__)
SessionFactory = get_session_factory()


async def promote_due_jobs() -> None:
    now = datetime.now(timezone.utc)
    async with SessionFactory() as session:
        jobs = list(
            (await session.scalars(
                select(Job)
                .where(Job.state == JobState.SCHEDULED, Job.available_at <= now)
                .with_for_update(skip_locked=True)
            )).all()
        )
        for job in jobs:
            job.state = JobState.QUEUED

        recurring = list(
            (await session.scalars(
                select(ScheduledJob)
                .where(ScheduledJob.enabled, ScheduledJob.next_run_at <= now)
                .with_for_update(skip_locked=True)
            )).all()
        )
        for schedule in recurring:
            template = await session.get(Job, schedule.job_template_id)
            if template:
                session.add(
                    Job(
                        queue_id=template.queue_id,
                        task_type=template.task_type,
                        payload=template.payload,
                        priority=template.priority,
                        state=JobState.QUEUED,
                        available_at=now,
                        scheduled_at=now,
                    )
                )
            schedule.last_run_at = now
            schedule.next_run_at = croniter(schedule.cron_expression, now).get_next(datetime)
        await session.commit()


async def main() -> None:
    while True:
        try:
            await promote_due_jobs()
        except Exception:
            logger.exception("scheduler iteration failed")
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
