from src.appointments.database import (
    initialize_database,
    seed_demo_data,
)

from src.appointments.service import (
    check_appointment,
    cancel_appointment,
    reschedule_appointment,
)


def setup_module():
    initialize_database()
    seed_demo_data()


def test_check_appointment():
    appointment = check_appointment(
        "HC-1001"
    )

    assert appointment is not None


def test_cancel_appointment():
    result = cancel_appointment(
        "HC-1001"
    )

    assert result["success"] is True
    assert result["status"] == "CANCELLED"


def test_unknown_appointment():
    result = cancel_appointment(
        "UNKNOWN"
    )

    assert result["success"] is False
