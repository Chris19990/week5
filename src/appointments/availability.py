from datetime import datetime, timedelta

from src.appointments.database import get_connection


# ============================================================
# CLINIC AVAILABILITY
# ============================================================

def get_clinic(clinic_name: str):
    """
    Return clinic information by name.
    """

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

    connection.close()

    if clinic is None:
        return None

    return dict(clinic)


# ============================================================
# DAILY APPOINTMENT COUNT
# ============================================================

def count_daily_appointments(
    clinic_name: str,
    appointment_date: str,
):
    """
    Count active appointments for a clinic on a given date.
    """

    connection = get_connection()

    cursor = connection.cursor()

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

    count = cursor.fetchone()[0]

    connection.close()

    return count


# ============================================================
# CHECK DAILY CAPACITY
# ============================================================

def check_daily_capacity(
    clinic_name: str,
    appointment_date: str,
):
    """
    Check whether the clinic can accept another appointment
    on the requested date.
    """

    clinic = get_clinic(clinic_name)

    if clinic is None:
        return {
            "available": False,
            "reason": "Clinic not found.",
        }

    current_count = count_daily_appointments(
        clinic_name,
        appointment_date,
    )

    daily_limit = clinic["daily_limit"]

    if current_count >= daily_limit:
        return {
            "available": False,
            "reason": (
                "The maximum number of appointments "
                "for this clinic on this day has been reached."
            ),
            "current_count": current_count,
            "daily_limit": daily_limit,
        }

    return {
        "available": True,
        "current_count": current_count,
        "daily_limit": daily_limit,
        "remaining": daily_limit - current_count,
    }


# ============================================================
# CHECK SPECIFIC SLOT
# ============================================================

def is_slot_available(
    clinic_name: str,
    appointment_date: str,
    appointment_time: str,
):
    """
    Check whether a specific appointment slot is available.
    """

    clinic = get_clinic(clinic_name)

    if clinic is None:
        return {
            "available": False,
            "reason": "Clinic not found.",
        }

    # --------------------------------------------------------
    # Validate date
    # --------------------------------------------------------

    try:
        requested_date = datetime.strptime(
            appointment_date,
            "%Y-%m-%d",
        ).date()

    except ValueError:

        return {
            "available": False,
            "reason": "Invalid date format. Use YYYY-MM-DD.",
        }

    # --------------------------------------------------------
    # Validate time
    # --------------------------------------------------------

    try:
        requested_time = datetime.strptime(
            appointment_time,
            "%H:%M",
        ).time()

    except ValueError:

        return {
            "available": False,
            "reason": "Invalid time format. Use HH:MM.",
        }

    # --------------------------------------------------------
    # Do not allow past dates
    # --------------------------------------------------------

    today = datetime.now().date()

    if requested_date < today:

        return {
            "available": False,
            "reason": "Appointments cannot be booked in the past.",
        }

    # --------------------------------------------------------
    # Check opening hours
    # --------------------------------------------------------

    weekday = requested_date.weekday()

    # Sunday
    if weekday == 6:

        return {
            "available": False,
            "reason": "The clinic is closed on Sundays.",
        }

    # Saturday
    if weekday == 5:

        opening = clinic["saturday_opening_time"]
        closing = clinic["saturday_closing_time"]

    else:

        opening = clinic["opening_time"]
        closing = clinic["closing_time"]

    opening_time = datetime.strptime(
        opening,
        "%H:%M",
    ).time()

    closing_time = datetime.strptime(
        closing,
        "%H:%M",
    ).time()

    if not (
        opening_time <= requested_time < closing_time
    ):

        return {
            "available": False,
            "reason": (
                f"The clinic is open from {opening} "
                f"to {closing} on this day."
            ),
        }

    # --------------------------------------------------------
    # Check daily capacity
    # --------------------------------------------------------

    capacity = check_daily_capacity(
        clinic_name,
        appointment_date,
    )

    if not capacity["available"]:

        return capacity

    # --------------------------------------------------------
    # Check existing appointment
    # --------------------------------------------------------

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT appointment_id
        FROM appointments
        WHERE clinic_location = ?
        AND appointment_date = ?
        AND appointment_time = ?
        AND status IN ('SCHEDULED', 'RESCHEDULED')
        """,
        (
            clinic_name,
            appointment_date,
            appointment_time,
        ),
    )

    existing = cursor.fetchone()

    connection.close()

    if existing:

        return {
            "available": False,
            "reason": "The requested time slot is already booked.",
        }

    return {
        "available": True,
        "clinic": clinic_name,
        "date": appointment_date,
        "time": appointment_time,
        "remaining_daily_capacity": capacity["remaining"],
    }


# ============================================================
# GET AVAILABLE SLOTS
# ============================================================

def get_available_slots(
    clinic_name: str,
    appointment_date: str,
    interval_minutes: int = 30,
):
    """
    Return available time slots for a clinic on a given date.
    """

    clinic = get_clinic(clinic_name)

    if clinic is None:
        return {
            "success": False,
            "message": "Clinic not found.",
            "slots": [],
        }

    try:
        requested_date = datetime.strptime(
            appointment_date,
            "%Y-%m-%d",
        ).date()

    except ValueError:

        return {
            "success": False,
            "message": "Invalid date format. Use YYYY-MM-DD.",
            "slots": [],
        }

    today = datetime.now().date()

    if requested_date < today:

        return {
            "success": False,
            "message": "Appointments cannot be booked in the past.",
            "slots": [],
        }

    # --------------------------------------------------------
    # Closed Sunday
    # --------------------------------------------------------

    if requested_date.weekday() == 6:

        return {
            "success": True,
            "message": "The clinic is closed on Sundays.",
            "slots": [],
        }

    # --------------------------------------------------------
    # Opening hours
    # --------------------------------------------------------

    if requested_date.weekday() == 5:

        opening = clinic["saturday_opening_time"]
        closing = clinic["saturday_closing_time"]

    else:

        opening = clinic["opening_time"]
        closing = clinic["closing_time"]

    start = datetime.strptime(
        opening,
        "%H:%M",
    )

    end = datetime.strptime(
        closing,
        "%H:%M",
    )

    slots = []

    current = start

    while current < end:

        time_string = current.strftime("%H:%M")

        result = is_slot_available(
            clinic_name,
            appointment_date,
            time_string,
        )

        if result["available"]:
            slots.append(time_string)

        current += timedelta(
            minutes=interval_minutes
        )

    return {
        "success": True,
        "clinic": clinic_name,
        "date": appointment_date,
        "slots": slots,
    }
