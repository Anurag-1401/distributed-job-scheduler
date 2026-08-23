import pytest

from app.tasks import execute_task


@pytest.mark.asyncio
async def test_echo_task():
    assert await execute_task("echo", {"message": "hello"}) == {"message": "hello"}


@pytest.mark.asyncio
async def test_unknown_task_is_rejected():
    with pytest.raises(ValueError):
        await execute_task("arbitrary_python", {})
