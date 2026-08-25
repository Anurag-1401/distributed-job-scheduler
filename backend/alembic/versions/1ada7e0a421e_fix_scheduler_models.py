"""fix scheduler models"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "1ada7e0a421e"
down_revision: Union[str, None] = "0002_unified_runtime_hardening"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # dead_letter_jobs
    # ------------------------------------------------------------------

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_dead_letter_jobs_worker_id
        ON dead_letter_jobs (worker_id)
    """)

    op.execute("""
        ALTER TABLE dead_letter_jobs
        DROP CONSTRAINT IF EXISTS dead_letter_jobs_worker_id_fkey
    """)

    op.execute("""
        ALTER TABLE dead_letter_jobs
        ADD CONSTRAINT dead_letter_jobs_worker_id_fkey
        FOREIGN KEY (worker_id)
        REFERENCES workers (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
    """)

    # ------------------------------------------------------------------
    # job_logs
    # ------------------------------------------------------------------

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_job_logs_timestamp
        ON job_logs (timestamp)
    """)

    op.execute("""
        ALTER TABLE job_logs
        DROP CONSTRAINT IF EXISTS job_logs_execution_id_fkey
    """)

    op.execute("""
        ALTER TABLE job_logs
        ADD CONSTRAINT job_logs_execution_id_fkey
        FOREIGN KEY (execution_id)
        REFERENCES job_executions (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
    """)

    # ------------------------------------------------------------------
    # jobs
    # ------------------------------------------------------------------

    op.execute("""
        DROP INDEX IF EXISTS ix_jobs_schedule_template
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_jobs_parent_job_id
        ON jobs (parent_job_id)
    """)

    op.execute("""
        ALTER TABLE jobs
        DROP CONSTRAINT IF EXISTS jobs_parent_job_id_fkey
    """)

    op.execute("""
        ALTER TABLE jobs
        DROP CONSTRAINT IF EXISTS jobs_batch_id_fkey
    """)

    op.execute("""
        ALTER TABLE jobs
        ADD CONSTRAINT jobs_batch_id_fkey
        FOREIGN KEY (batch_id)
        REFERENCES jobs (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
    """)

    op.execute("""
        ALTER TABLE jobs
        ADD CONSTRAINT jobs_parent_job_id_fkey
        FOREIGN KEY (parent_job_id)
        REFERENCES jobs (id)
        ON UPDATE CASCADE
        ON DELETE SET NULL
    """)

    # ------------------------------------------------------------------
    # projects
    # ------------------------------------------------------------------

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_projects_slug
        ON projects (slug)
    """)

    # ------------------------------------------------------------------
    # queues
    # ------------------------------------------------------------------

    op.alter_column(
        "queues",
        "name",
        existing_type=sa.VARCHAR(length=120),
        type_=sa.String(length=200),
        existing_nullable=False,
    )

    # The old index may or may not exist depending on the schema created
    # by the previous migrations, so use IF EXISTS.
    op.execute("""
        DROP INDEX IF EXISTS ix_queue_project_status
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_queues_status
        ON queues (status)
    """)

    # ------------------------------------------------------------------
    # retry_policies
    # ------------------------------------------------------------------

    op.alter_column(
        "retry_policies",
        "queue_id",
        existing_type=sa.UUID(),
        nullable=False,
    )

    op.execute("""
        ALTER TABLE retry_policies
        DROP CONSTRAINT IF EXISTS uq_retry_policy_queue
    """)

    op.execute("""
        DROP INDEX IF EXISTS ix_retry_policies_queue_id
    """)

    op.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS ix_retry_policies_queue_id
        ON retry_policies (queue_id)
    """)


def downgrade() -> None:
    # ------------------------------------------------------------------
    # retry_policies
    # ------------------------------------------------------------------

    op.execute("""
        DROP INDEX IF EXISTS ix_retry_policies_queue_id
    """)

    op.execute("""
        ALTER TABLE retry_policies
        ADD CONSTRAINT uq_retry_policy_queue
        UNIQUE (queue_id)
    """)

    op.alter_column(
        "retry_policies",
        "queue_id",
        existing_type=sa.UUID(),
        nullable=True,
    )

    # ------------------------------------------------------------------
    # queues
    # ------------------------------------------------------------------

    op.execute("""
        ALTER TABLE queues
        ADD COLUMN IF NOT EXISTS created_at
        TIMESTAMP WITH TIME ZONE
        DEFAULT now()
        NOT NULL
    """)

    op.execute("""
        ALTER TABLE queues
        ADD COLUMN IF NOT EXISTS updated_at
        TIMESTAMP WITH TIME ZONE
        DEFAULT now()
        NOT NULL
    """)

    op.execute("""
        DROP INDEX IF EXISTS ix_queues_status
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_queue_project_status
        ON queues (project_id, status)
    """)

    op.alter_column(
        "queues",
        "name",
        existing_type=sa.String(length=200),
        type_=sa.VARCHAR(length=120),
        existing_nullable=False,
    )

    # ------------------------------------------------------------------
    # projects
    # ------------------------------------------------------------------

    op.execute("""
        DROP INDEX IF EXISTS ix_projects_slug
    """)

    # ------------------------------------------------------------------
    # jobs
    # ------------------------------------------------------------------

    op.execute("""
        ALTER TABLE jobs
        DROP CONSTRAINT IF EXISTS jobs_parent_job_id_fkey
    """)

    op.execute("""
        ALTER TABLE jobs
        DROP CONSTRAINT IF EXISTS jobs_batch_id_fkey
    """)

    op.execute("""
        ALTER TABLE jobs
        ADD CONSTRAINT jobs_batch_id_fkey
        FOREIGN KEY (batch_id)
        REFERENCES jobs (id)
        ON DELETE SET NULL
    """)

    op.execute("""
        ALTER TABLE jobs
        ADD CONSTRAINT jobs_parent_job_id_fkey
        FOREIGN KEY (parent_job_id)
        REFERENCES jobs (id)
        ON UPDATE CASCADE
        ON DELETE CASCADE
    """)

    op.execute("""
        DROP INDEX IF EXISTS ix_jobs_parent_job_id
    """)

    op.execute("""
        CREATE INDEX IF NOT EXISTS ix_jobs_schedule_template
        ON jobs (is_schedule_template)
    """)

    # ------------------------------------------------------------------
    # job_logs
    # ------------------------------------------------------------------

    op.execute("""
        ALTER TABLE job_logs
        DROP CONSTRAINT IF EXISTS job_logs_execution_id_fkey
    """)

    op.execute("""
        ALTER TABLE job_logs
        ADD CONSTRAINT job_logs_execution_id_fkey
        FOREIGN KEY (execution_id)
        REFERENCES job_executions (id)
        ON DELETE CASCADE
    """)

    op.execute("""
        DROP INDEX IF EXISTS ix_job_logs_timestamp
    """)

    # ------------------------------------------------------------------
    # dead_letter_jobs
    # ------------------------------------------------------------------

    op.execute("""
        ALTER TABLE dead_letter_jobs
        DROP CONSTRAINT IF EXISTS dead_letter_jobs_worker_id_fkey
    """)

    op.execute("""
        ALTER TABLE dead_letter_jobs
        ADD CONSTRAINT dead_letter_jobs_worker_id_fkey
        FOREIGN KEY (worker_id)
        REFERENCES workers (id)
        ON DELETE SET NULL
    """)

    op.execute("""
        DROP INDEX IF EXISTS ix_dead_letter_jobs_worker_id
    """)