import random

from app.models import BackoffStrategy, RetryPolicy


def retry_delay(policy: RetryPolicy, attempt_number: int) -> int:
    if policy.strategy == BackoffStrategy.FIXED:
        delay = policy.base_delay_seconds
    elif policy.strategy == BackoffStrategy.LINEAR:
        delay = policy.base_delay_seconds * attempt_number
    else:
        delay = policy.base_delay_seconds * (2 ** max(attempt_number - 1, 0))
    delay = min(delay, policy.max_delay_seconds)
    if policy.jitter and delay:
        delay += random.uniform(0, max(delay * 0.1, 1))
    return max(0, int(delay))
