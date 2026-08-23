from app.models import BackoffStrategy, JobState, QueueStatus, Role


def test_enum_values_are_strings():
    assert Role.OWNER.value == "OWNER"
    assert QueueStatus.ACTIVE.value == "ACTIVE"
    assert JobState.QUEUED.value == "QUEUED"
    assert BackoffStrategy.EXPONENTIAL.value == "EXPONENTIAL"


def test_state_machine_transitions_documented():
    expected = {
        "SCHEDULED", "QUEUED", "CLAIMED", "RUNNING", "COMPLETED",
        "FAILED", "RETRYING", "CANCELLED", "DEAD_LETTER",
    }
    assert {state.value for state in JobState} == expected
