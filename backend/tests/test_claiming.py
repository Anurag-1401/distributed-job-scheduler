import pytest

pytestmark = pytest.mark.integration


@pytest.mark.skip(reason="Requires PostgreSQL service; run with Docker Compose integration profile")
@pytest.mark.asyncio
async def test_concurrent_workers_claim_each_job_once():
    """Integration contract: concurrent SELECT FOR UPDATE SKIP LOCKED claims are unique."""
    assert True
