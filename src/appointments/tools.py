from src.appointments.service import (
    check_appointment,
    cancel_appointment,
    reschedule_appointment,
)
from src.appointments.service import (
    check_appointment,
    cancel_appointment,
    reschedule_appointment,
    book_appointment,
)


def tool_check_appointment(
    appointment_id: str,
):
    return check_appointment(
        appointment_id
    )


def tool_cancel_appointment(
    appointment_id: str,
):
    return cancel_appointment(
        appointment_id
    )


def tool_reschedule_appointment(
    appointment_id: str,
    new_date: str,
    new_time: str,
):
    return reschedule_appointment(
        appointment_id,
        new_date,
        new_time,
    )
def tool_book_appointment(
    patient_id: str,
    patient_name: str,
    clinic_name: str,
    service_name: str,
    appointment_date: str,
    appointment_time: str,
):
    return book_appointment(
        patient_id,
        patient_name,
        clinic_name,
        service_name,
        appointment_date,
        appointment_time,
    )
