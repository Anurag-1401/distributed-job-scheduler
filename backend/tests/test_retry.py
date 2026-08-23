from types import SimpleNamespace

from app.models import BackoffStrategy
from app.services.retry import retry_delay


def test_backoff_is_bounded():
    policy = SimpleNamespace(
        strategy=BackoffStrategy.EXPONENTIAL, base_delay_seconds=2, max_delay_seconds=8
    )
    assert retry_delay(policy, 4, jitter=False) == 8


def test_fixed_backoff():
    policy = SimpleNamespace(
        strategy=BackoffStrategy.FIXED, base_delay_seconds=10, max_delay_seconds=100
    )
    assert retry_delay(policy, 3, jitter=False) == 10


def test_linear_backoff():
    policy = SimpleNamespace(
        strategy=BackoffStrategy.LINEAR, base_delay_seconds=10, max_delay_seconds=100
    )
    assert retry_delay(policy, 3, jitter=False) == 30
