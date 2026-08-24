from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models import BackoffStrategy, JobState, JobType, QueueStatus, Role


class ErrorBody(BaseModel):
    code: str
    message: str
    details: dict = {}


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=128)
    full_name: str = Field(min_length=1, max_length=200)

 
class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    email: EmailStr
    full_name: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead


class OrganizationCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    slug: str | None = Field(default=None, pattern=r"^[a-z0-9-]+$", max_length=120)
    description: str | None = Field(default=None, max_length=500)


class OrganizationRead(OrganizationCreate):
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime | None = None
    id: UUID
 

class ProjectCreate(BaseModel):
    organization_id: UUID
    name: str = Field(min_length=1, max_length=200)
    slug: str | None = Field(default=None, pattern=r"^[a-z0-9-]+$", max_length=120)
    description: str | None = Field(default=None, max_length=500)


class ProjectPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = Field(default=None, max_length=500)


class ProjectRead(ProjectCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID


class RetryPolicyCreate(BaseModel):
    max_attempts: int = Field(default=3, ge=1, le=100)
    base_delay_seconds: int = Field(default=10, ge=0, le=86400)
    max_delay_seconds: int = Field(default=3600, ge=0, le=604800)
    strategy: BackoffStrategy = BackoffStrategy.EXPONENTIAL
    jitter: bool = True


class RetryPolicyRead(RetryPolicyCreate):
    model_config = ConfigDict(from_attributes=True)
    id: UUID


class QueueCreate(BaseModel):
    project_id: UUID
    name: str = Field(min_length=1, max_length=120)
    priority: int = Field(default=0, ge=-100, le=100)
    concurrency_limit: int = Field(default=1, ge=1, le=10000)
    retry_policy: RetryPolicyCreate = Field(default_factory=RetryPolicyCreate)


class QueuePatch(BaseModel):
    priority: int | None = Field(default=None, ge=-100, le=100)
    concurrency_limit: int | None = Field(default=None, ge=1, le=10000)
    status: QueueStatus | None = None
    retry_policy: RetryPolicyCreate | None = None


class QueueRead(BaseModel):
    id: UUID
    project_id: UUID
    retry_policy_id: UUID
    name: str
    priority: int
    concurrency_limit: int
    status: QueueStatus
    retry_policy: RetryPolicyRead | None = None
    stats: dict = Field(default_factory=dict)


class JobCreate(BaseModel):
    queue_id: UUID
    type: JobType = JobType.IMMEDIATE
    task_type: str = Field(default="echo", min_length=1, max_length=80)
    payload: dict = Field(default_factory=dict)
    priority: int = Field(default=0, ge=-100, le=100)
    delay_seconds: float | None = Field(default=None, ge=0.1, le=604800)
    scheduled_at: datetime | None = None
    cron_expression: str | None = None
    timezone: str = "UTC"
    idempotency_key: str | None = Field(default=None, max_length=200)

    @field_validator("scheduled_at")
    @classmethod
    def scheduled_time_is_aware(cls, value: datetime | None) -> datetime | None:
        if value is not None and value.tzinfo is None:
            raise ValueError("scheduled_at must include a timezone")
        return value


class BatchJobItem(BaseModel):
    task_type: str = Field(default="echo", min_length=1, max_length=80)
    payload: dict = Field(default_factory=dict)
    priority: int = Field(default=0, ge=-100, le=100)


class BatchJobCreate(BaseModel):
    queue_id: UUID
    priority: int = Field(default=0, ge=-100, le=100)
    jobs: list[BatchJobItem] = Field(min_length=1, max_length=1000)


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    queue_id: UUID
    task_type: str
    job_type: JobType
    type: JobType
    payload: dict
    priority: int
    state: JobState
    status: JobState
    scheduled_at: datetime | None
    available_at: datetime
    claimed_at: datetime | None
    attempts: int
    worker_id: UUID | None
    last_error: str | None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    queue_name: str | None = None
    dead_letter_id: UUID | None = None


class Page(BaseModel):
    items: list
    page: int
    limit: int
    total: int


class WorkerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    worker_key: str
    status: str
    max_concurrency: int
    current_job_count: int
    last_heartbeat_at: datetime
    utilization: float = 0


class ExecutionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    job_id: UUID
    worker_id: UUID | None
    attempt_number: int
    status: str
    started_at: datetime
    completed_at: datetime | None
    duration_ms: int | None
    error: str | None
    result_metadata: dict | None


class LogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    job_id: UUID
    execution_id: UUID | None
    timestamp: datetime
    level: str
    message: str
    metadata_json: dict | None
