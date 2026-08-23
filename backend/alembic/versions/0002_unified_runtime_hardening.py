"""Add unified-runtime fields and frontend contract compatibility."""
from alembic import op

revision = "0002_unified_runtime_hardening"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""DO $$ BEGIN CREATE TYPE job_type AS ENUM ('IMMEDIATE','DELAYED','SCHEDULED','CRON','BATCH'); EXCEPTION WHEN duplicate_object THEN NULL; END $$;""")
    op.execute("ALTER TABLE retry_policies ADD COLUMN IF NOT EXISTS jitter BOOLEAN NOT NULL DEFAULT TRUE")
    op.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS job_type job_type NOT NULL DEFAULT 'IMMEDIATE'")
    op.execute("ALTER TABLE jobs ADD COLUMN IF NOT EXISTS is_schedule_template BOOLEAN NOT NULL DEFAULT FALSE")
    op.execute("ALTER TABLE organizations ADD COLUMN IF NOT EXISTS description TEXT")
    op.execute("ALTER TABLE projects ADD COLUMN IF NOT EXISTS description TEXT")
    op.execute("CREATE INDEX IF NOT EXISTS ix_jobs_job_type ON jobs (job_type)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_jobs_schedule_template ON jobs (is_schedule_template)")


def downgrade() -> None:
    raise RuntimeError("Downgrade is intentionally disabled to protect scheduler data")
