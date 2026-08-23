from datetime import datetime

import pytest

from app.schemas import JobCreate


def test_job_create_rejects_naive_scheduled_at():
    with pytest.raises(ValueError):
        JobCreate(task_type="echo", payload={}, scheduled_at=datetime(2026, 1, 1, 12, 0, 0))
