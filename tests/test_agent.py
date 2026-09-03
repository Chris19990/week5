from src.agent.router import (
    Intent,
    route_intent,
)


def test_cancel_intent():
    result = route_intent(
        "I want to cancel my appointment"
    )

    assert result == Intent.CANCEL_APPOINTMENT


def test_reschedule_intent():
    result = route_intent(
        "I need to reschedule my appointment"
    )

    assert result == Intent.RESCHEDULE_APPOINTMENT


def test_medical_intent():
    result = route_intent(
        "Can you diagnose my symptoms?"
    )

    assert result == Intent.MEDICAL_REQUEST


def test_hours_intent():
    result = route_intent(
        "What time does the clinic open?"
    )

    assert result == Intent.OPENING_HOURS
