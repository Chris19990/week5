from src.safety.guardrails import safety_check


def test_medical_request_is_blocked():
    result = safety_check(
        "Can you diagnose my symptoms?"
    )

    assert result["blocked"] is True


def test_emergency_request_is_blocked():
    result = safety_check(
        "I am having an emergency"
    )

    assert result["blocked"] is True


def test_normal_request_is_not_blocked():
    result = safety_check(
        "What time does the clinic open?"
    )

    assert result["blocked"] is False
