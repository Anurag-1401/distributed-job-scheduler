import pytest


@pytest.fixture
def integration_database_url() -> str:
    return "postgresql+asyncpg://scheduler:scheduler@localhost:5432/scheduler"
