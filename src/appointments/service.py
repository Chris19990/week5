from datetime import datetime

from src.appointments.database import get_connection


def check_appointment(
    appointment_id: str,
):
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM appointments
        WHERE appointment_id = ?
        """,
        (appointment_id,),
    )

    appointment = cursor.fetchone()

    connection.close()

    if appointment is None:
        return None

    return dict(appointment)


def cancel_appointment(
    appointment_id: str,
):
    appointment = check_appointment(
        appointment_id
    )

    if appointment is None:
        return {
            "success": False,
            "message": "Appointment not found.",
        }

    if appointment["status"] == "CANCELLED":
        return {
            "success": False,
            "message": "Appointment is already cancelled.",
        }

    now = datetime.now().isoformat()

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        UPDATE appointments
        SET status = ?,
            updated_at = ?
        WHERE appointment_id = ?
        """,
        (
            "CANCELLED",
            now,
            appointment_id,
        ),
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "appointment_id": appointment_id,
        "status": "CANCELLED",
    }


def reschedule_appointment(
    appointment_id: str,
    new_date: str,
    new_time: str,
):
    appointment = check_appointment(
        appointment_id
    )

    if appointment is None:
        return {
            "success": False,
            "message": "Appointment not found.",
        }

    if appointment["status"] == "CANCELLED":
        return {
            "success": False,
            "message": "Cancelled appointments cannot be rescheduled.",
        }

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT appointment_id
        FROM appointments
        WHERE appointment_date = ?
        AND appointment_time = ?
        AND status IN ('SCHEDULED', 'RESCHEDULED')
        """,
        (
            new_date,
            new_time,
        ),
    )

    existing = cursor.fetchone()

    if existing:
        connection.close()

        return {
            "success": False,
            "message": "The requested slot is unavailable.",
        }

    now = datetime.now().isoformat()

    cursor.execute(
        """
        UPDATE appointments
        SET appointment_date = ?,
            appointment_time = ?,
            status = ?,
            updated_at = ?
        WHERE appointment_id = ?
        """,
        (
            new_date,
            new_time,
            "RESCHEDULED",
            now,
            appointment_id,
        ),
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "appointment_id": appointment_id,
        "new_date": new_date,
        "new_time": new_time,
        "status": "RESCHEDULED",
    }
def book_appointment(
    patient_id: str,
    patient_name: str,
    clinic_name: str,
    service_name: str,
    appointment_date: str,
    appointment_time: str,
):
    """
    Create a new appointment after validating:
    - clinic
    - service
    - date/time
    - opening hours
    - daily capacity
    - overlapping appointments
    """

    from datetime import datetime, timedelta

    # ========================================================
    # VALIDATE CLINIC
    # ========================================================

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT *
        FROM clinics
        WHERE name = ?
        AND active = 1
        """,
        (clinic_name,),
    )

    clinic = cursor.fetchone()

    if clinic is None:
        connection.close()

        return {
            "success": False,
            "message": "Clinic not found.",
        }

    # ========================================================
    # VALIDATE SERVICE
    # ========================================================

    cursor.execute(
        """
        SELECT *
        FROM services
        WHERE name = ?
        AND active = 1
        """,
        (service_name,),
    )

    service = cursor.fetchone()

    if service is None:
        connection.close()

        return {
            "success": False,
            "message": "Service not found.",
        }

    duration_minutes = service["duration_minutes"]

    # ========================================================
    # VALIDATE DATE
    # ========================================================

    try:

        requested_date = datetime.strptime(
            appointment_date,
            "%Y-%m-%d",
        ).date()

    except ValueError:

        connection.close()

        return {
            "success": False,
            "message": "Invalid date format. Use YYYY-MM-DD.",
        }

    if requested_date < datetime.now().date():

        connection.close()

        return {
            "success": False,
            "message": "Appointments cannot be booked in the past.",
        }

    # ========================================================
    # VALIDATE TIME
    # ========================================================

    try:

        start_datetime = datetime.strptime(
            f"{appointment_date} {appointment_time}",
            "%Y-%m-%d %H:%M",
        )

    except ValueError:

        connection.close()

        return {
            "success": False,
            "message": "Invalid date or time format.",
        }

    end_datetime = start_datetime + timedelta(
        minutes=duration_minutes
    )

    # ========================================================
    # CLOSED SUNDAY
    # ========================================================

    if requested_date.weekday() == 6:

        connection.close()

        return {
            "success": False,
            "message": "The clinic is closed on Sundays.",
        }

    # ========================================================
    # OPENING HOURS
    # ========================================================

    if requested_date.weekday() == 5:

        opening = clinic["saturday_opening_time"]
        closing = clinic["saturday_closing_time"]

    else:

        opening = clinic["opening_time"]
        closing = clinic["closing_time"]

    opening_datetime = datetime.strptime(
        f"{appointment_date} {opening}",
        "%Y-%m-%d %H:%M",
    )

    closing_datetime = datetime.strptime(
        f"{appointment_date} {closing}",
        "%Y-%m-%d %H:%M",
    )

    if (
        start_datetime < opening_datetime
        or end_datetime > closing_datetime
    ):

        connection.close()

        return {
            "success": False,
            "message": (
                f"The requested appointment must be within "
                f"clinic opening hours ({opening} - {closing})."
            ),
        }

    # ========================================================
    # DAILY CAPACITY
    # ========================================================

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM appointments
        WHERE clinic_location = ?
        AND appointment_date = ?
        AND status IN ('SCHEDULED', 'RESCHEDULED')
        """,
        (
            clinic_name,
            appointment_date,
        ),
    )

    current_count = cursor.fetchone()[0]

    if current_count >= clinic["daily_limit"]:

        connection.close()

        return {
            "success": False,
            "message": (
                "The maximum number of appointments "
                "for this clinic on this day has been reached."
            ),
        }

    # ========================================================
    # CHECK OVERLAPPING APPOINTMENTS
    # ========================================================

    cursor.execute(
        """
        SELECT appointment_id, appointment_time, service
        FROM appointments
        WHERE clinic_location = ?
        AND appointment_date = ?
        AND status IN ('SCHEDULED', 'RESCHEDULED')
        """,
        (
            clinic_name,
            appointment_date,
        ),
    )

    existing_appointments = cursor.fetchall()

    for existing in existing_appointments:

        existing_time = datetime.strptime(
            f"{appointment_date} {existing['appointment_time']}",
            "%Y-%m-%d %H:%M",
        )

        # Find duration of existing service
        cursor.execute(
            """
            SELECT duration_minutes
            FROM services
            WHERE name = ?
            """,
            (existing["service"],),
        )

        existing_service = cursor.fetchone()

        if existing_service is None:
            existing_duration = 30
        else:
            existing_duration = existing_service["duration_minutes"]

        existing_end = (
            existing_time
            + timedelta(minutes=existing_duration)
        )

        # Overlap test
        if (
            start_datetime < existing_end
            and end_datetime > existing_time
        ):

            connection.close()

            return {
                "success": False,
                "message": (
                    "The requested time slot overlaps "
                    "with an existing appointment."
                ),
            }

    # ========================================================
    # GENERATE APPOINTMENT ID
    # ========================================================

    cursor.execute(
        """
        SELECT appointment_id
        FROM appointments
        WHERE appointment_id LIKE 'HC-%'
        """
    )

    existing_ids = cursor.fetchall()

    numbers = []

    for row in existing_ids:

        try:

            number = int(
                row["appointment_id"].replace(
                    "HC-",
                    "",
                )
            )

            numbers.append(number)

        except ValueError:
            pass

    if numbers:
        next_number = max(numbers) + 1
    else:
        next_number = 1001

    appointment_id = f"HC-{next_number}"

    # ========================================================
    # CREATE APPOINTMENT
    # ========================================================

    now = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO appointments (
            appointment_id,
            patient_id,
            patient_name,
            clinic_location,
            service,
            appointment_date,
            appointment_time,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            appointment_id,
            patient_id,
            patient_name,
            clinic_name,
            service_name,
            appointment_date,
            appointment_time,
            "SCHEDULED",
            now,
            now,
        ),
    )

    connection.commit()
    connection.close()

    return {
        "success": True,
        "appointment_id": appointment_id,
        "patient_id": patient_id,
        "patient_name": patient_name,
        "clinic": clinic_name,
        "service": service_name,
        "date": appointment_date,
        "time": appointment_time,
        "duration_minutes": duration_minutes,
        "status": "SCHEDULED",
    }
