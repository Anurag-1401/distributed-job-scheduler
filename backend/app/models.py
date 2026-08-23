import enum
import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


# ============================================================
# ENUMS
# ============================================================


class Role(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    DEVELOPER = "DEVELOPER"
    VIEWER = "VIEWER"


class QueueStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"


class JobType(str, enum.Enum):
    IMMEDIATE = "IMMEDIATE"
    DELAYED = "DELAYED"
    SCHEDULED = "SCHEDULED"
    CRON = "CRON"
    BATCH = "BATCH"


class JobState(str, enum.Enum):
    SCHEDULED = "SCHEDULED"
    QUEUED = "QUEUED"
    CLAIMED = "CLAIMED"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    RETRYING = "RETRYING"
    CANCELLED = "CANCELLED"
    DEAD_LETTER = "DEAD_LETTER"


class ExecutionStatus(str, enum.Enum):
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class WorkerStatus(str, enum.Enum):
    ONLINE = "ONLINE"
    OFFLINE = "OFFLINE"
    DRAINING = "DRAINING"


class LogLevel(str, enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class BackoffStrategy(str, enum.Enum):
    FIXED = "FIXED"
    LINEAR = "LINEAR"
    EXPONENTIAL = "EXPONENTIAL"


# ============================================================
# TIMESTAMP MIXIN
# ============================================================


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# ============================================================
# USER
# ============================================================


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    email: Mapped[str] = mapped_column(
        String(320),
        unique=True,
        index=True,
        nullable=False,
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    full_name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    organizations: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="user",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ============================================================
# ORGANIZATION
# ============================================================


class Organization(TimestampMixin, Base):
    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(120),
        unique=True,
        index=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    members: Mapped[list["OrganizationMember"]] = relationship(
        "OrganizationMember",
        back_populates="organization",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    projects: Mapped[list["Project"]] = relationship(
        "Project",
        back_populates="organization",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ============================================================
# ORGANIZATION MEMBER
# ============================================================


class OrganizationMember(TimestampMixin, Base):
    __tablename__ = "organization_members"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_org_member",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    role: Mapped[Role] = mapped_column(
        Enum(
            Role,
            name="role",
        ),
        default=Role.DEVELOPER,
        nullable=False,
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="members",
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="organizations",
    )


# ============================================================
# PROJECT
# ============================================================


class Project(TimestampMixin, Base):
    __tablename__ = "projects"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "slug",
            name="uq_project_org_slug",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    organization_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    slug: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        index=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    organization: Mapped["Organization"] = relationship(
        "Organization",
        back_populates="projects",
    )

    queues: Mapped[list["Queue"]] = relationship(
        "Queue",
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ============================================================
# QUEUE
# ============================================================


class Queue(TimestampMixin, Base):
    __tablename__ = "queues"

    __table_args__ = (
        UniqueConstraint(
            "project_id",
            "name",
            name="uq_queue_project_name",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "projects.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    concurrency_limit: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
    )

    status: Mapped[QueueStatus] = mapped_column(
        Enum(
            QueueStatus,
            name="queue_status",
        ),
        default=QueueStatus.ACTIVE,
        nullable=False,
        index=True,
    )

    project: Mapped["Project"] = relationship(
        "Project",
        back_populates="queues",
    )

    jobs: Mapped[list["Job"]] = relationship(
        "Job",
        back_populates="queue",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    retry_policy: Mapped["RetryPolicy | None"] = relationship(
        "RetryPolicy",
        back_populates="queue",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

# ============================================================
# RETRY POLICY
# ============================================================


class RetryPolicy(TimestampMixin, Base):
    __tablename__ = "retry_policies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    queue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "queues.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        unique=True,
        index=True,
    )

    max_attempts: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False,
    )

    base_delay_seconds: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    max_delay_seconds: Mapped[int] = mapped_column(
        Integer,
        default=300,
        nullable=False,
    )

    strategy: Mapped[BackoffStrategy] = mapped_column(
        Enum(
            BackoffStrategy,
            name="backoff_strategy",
        ),
        default=BackoffStrategy.EXPONENTIAL,
        nullable=False,
    )

    jitter: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    queue: Mapped["Queue"] = relationship(
        "Queue",
        back_populates="retry_policy",
    )


# ============================================================
# JOB
# ============================================================


class Job(TimestampMixin, Base):
    __tablename__ = "jobs"

    __table_args__ = (
        Index(
            "ix_jobs_claim",
            "queue_id",
            "state",
            "available_at",
            "priority",
        ),
        UniqueConstraint(
            "queue_id",
            "idempotency_key",
            name="uq_job_idempotency",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    queue_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "queues.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    batch_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "jobs.id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    parent_job_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "jobs.id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    task_type: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
    )

    job_type: Mapped[JobType] = mapped_column(
        Enum(
            JobType,
            name="job_type",
        ),
        default=JobType.IMMEDIATE,
        nullable=False,
        index=True,
    )

    is_schedule_template: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        index=True,
    )

    payload: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    state: Mapped[JobState] = mapped_column(
        Enum(
            JobState,
            name="job_state",
        ),
        default=JobState.QUEUED,
        nullable=False,
        index=True,
    )

    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )

    available_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    worker_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "workers.id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    claimed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    last_error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    idempotency_key: Mapped[str | None] = mapped_column(
        String(200),
        nullable=True,
    )

    queue: Mapped["Queue"] = relationship(
        "Queue",
        back_populates="jobs",
    )

    worker: Mapped["Worker | None"] = relationship(
        "Worker",
        back_populates="jobs",
    )

    # --------------------------------------------------------
    # Batch relationship
    # --------------------------------------------------------

    batch_parent: Mapped["Job | None"] = relationship(
        "Job",
        foreign_keys=[batch_id],
        remote_side="Job.id",
        back_populates="batch_children",
    )

    batch_children: Mapped[list["Job"]] = relationship(
        "Job",
        foreign_keys=[batch_id],
        back_populates="batch_parent",
        passive_deletes=True,
    )

    # --------------------------------------------------------
    # Parent / child relationship
    # --------------------------------------------------------

    parent_job: Mapped["Job | None"] = relationship(
        "Job",
        foreign_keys=[parent_job_id],
        remote_side="Job.id",
        back_populates="child_jobs",
    )

    child_jobs: Mapped[list["Job"]] = relationship(
        "Job",
        foreign_keys=[parent_job_id],
        back_populates="parent_job",
        passive_deletes=True,
    )

    # --------------------------------------------------------
    # Execution / logs
    # --------------------------------------------------------

    executions: Mapped[list["JobExecution"]] = relationship(
        "JobExecution",
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    logs: Mapped[list["JobLog"]] = relationship(
        "JobLog",
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # --------------------------------------------------------
    # Scheduling
    # --------------------------------------------------------

    scheduled_job: Mapped["ScheduledJob | None"] = relationship(
        "ScheduledJob",
        back_populates="job_template",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )

    # --------------------------------------------------------
    # Dead letter
    # --------------------------------------------------------

    dead_letter: Mapped["DeadLetterJob | None"] = relationship(
        "DeadLetterJob",
        back_populates="job",
        cascade="all, delete-orphan",
        passive_deletes=True,
        uselist=False,
    )


# ============================================================
# JOB EXECUTION
# ============================================================


class JobExecution(Base):
    __tablename__ = "job_executions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "jobs.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    worker_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "workers.id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    attempt_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    status: Mapped[ExecutionStatus] = mapped_column(
        Enum(
            ExecutionStatus,
            name="execution_status",
        ),
        nullable=False,
    )

    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    duration_ms: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    error: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    result_metadata: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    job: Mapped["Job"] = relationship(
        "Job",
        back_populates="executions",
    )

    worker: Mapped["Worker | None"] = relationship(
        "Worker",
        back_populates="executions",
    )

    logs: Mapped[list["JobLog"]] = relationship(
        "JobLog",
        back_populates="execution",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


# ============================================================
# JOB LOG
# ============================================================


class JobLog(Base):
    __tablename__ = "job_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "jobs.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    execution_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "job_executions.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    level: Mapped[LogLevel] = mapped_column(
        Enum(
            LogLevel,
            name="log_level",
        ),
        nullable=False,
    )

    message: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    job: Mapped["Job"] = relationship(
        "Job",
        back_populates="logs",
    )

    execution: Mapped["JobExecution | None"] = relationship(
        "JobExecution",
        back_populates="logs",
    )


# ============================================================
# WORKER
# ============================================================


class Worker(TimestampMixin, Base):
    __tablename__ = "workers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    worker_key: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        index=True,
        nullable=False,
    )

    status: Mapped[WorkerStatus] = mapped_column(
        Enum(
            WorkerStatus,
            name="worker_status",
        ),
        default=WorkerStatus.ONLINE,
        nullable=False,
    )

    max_concurrency: Mapped[int] = mapped_column(
        Integer,
        default=10,
        nullable=False,
    )

    current_job_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    last_heartbeat_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    jobs: Mapped[list["Job"]] = relationship(
        "Job",
        back_populates="worker",
        passive_deletes=True,
    )

    executions: Mapped[list["JobExecution"]] = relationship(
        "JobExecution",
        back_populates="worker",
        passive_deletes=True,
    )

    heartbeats: Mapped[list["WorkerHeartbeat"]] = relationship(
        "WorkerHeartbeat",
        back_populates="worker",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    dead_letter_jobs: Mapped[list["DeadLetterJob"]] = relationship(
        "DeadLetterJob",
        back_populates="worker",
        passive_deletes=True,
    )


# ============================================================
# WORKER HEARTBEAT
# ============================================================


class WorkerHeartbeat(Base):
    __tablename__ = "worker_heartbeats"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    worker_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "workers.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )

    status: Mapped[WorkerStatus] = mapped_column(
        Enum(
            WorkerStatus,
            name="worker_status",
        ),
        nullable=False,
    )

    current_job_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    metadata_json: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True,
    )

    worker: Mapped["Worker"] = relationship(
        "Worker",
        back_populates="heartbeats",
    )


# ============================================================
# SCHEDULED JOB
# ============================================================


class ScheduledJob(Base):
    __tablename__ = "scheduled_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    job_template_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "jobs.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        unique=True,
    )

    cron_expression: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
    )

    timezone: Mapped[str] = mapped_column(
        String(80),
        default="UTC",
        nullable=False,
    )

    next_run_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    last_run_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
        index=True,
    )

    job_template: Mapped["Job"] = relationship(
        "Job",
        back_populates="scheduled_job",
    )


# ============================================================
# DEAD LETTER JOB
# ============================================================


class DeadLetterJob(Base):
    __tablename__ = "dead_letter_jobs"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    job_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "jobs.id",
            ondelete="CASCADE",
            onupdate="CASCADE",
        ),
        nullable=False,
        unique=True,
    )

    failure_reason: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    final_error: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    attempts: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    worker_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey(
            "workers.id",
            ondelete="SET NULL",
            onupdate="CASCADE",
        ),
        nullable=True,
        index=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    job: Mapped["Job"] = relationship(
        "Job",
        back_populates="dead_letter",
    )

    worker: Mapped["Worker | None"] = relationship(
        "Worker",
        back_populates="dead_letter_jobs",
    )