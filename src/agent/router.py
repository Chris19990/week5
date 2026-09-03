"""
Intent classification for HealthConnect Assistant.
"""

MEDICAL_KEYWORDS = [
    "diagnose",
    "diagnosis",
    "illness",
    "disease",
    "symptom",
    "symptoms",
    "pain",
    "treatment",
    "medicine",
    "medication",
    "drug",
    "prescription",
]

EMERGENCY_KEYWORDS = [
    "emergency",
    "chest pain",
    "difficulty breathing",
    "can't breathe",
    "cannot breathe",
    "severe bleeding",
    "unconscious",
    "stroke",
    "heart attack",
]

APPOINTMENT_KEYWORDS = [
    "appointment",
    "booking",
    "book",
    "schedule",
    "reschedule",
    "cancel",
    "cancellation",
    "late",
    "missed appointment",
]


def classify_intent(text):

    text_lower = text.lower()

    # Emergency must be checked first.
    for keyword in EMERGENCY_KEYWORDS:

        if keyword in text_lower:
            return "emergency"

    # Medical questions.
    for keyword in MEDICAL_KEYWORDS:

        if keyword in text_lower:
            return "medical"

    # Appointment-related questions.
    for keyword in APPOINTMENT_KEYWORDS:

        if keyword in text_lower:
            return "appointment"

    # General clinic information.
    return "general"
def classify_appointment_action(text):
    text_lower = text.lower()

    # ========================================================
    # CANCEL
    # ========================================================

    if (
        "cancel" in text_lower or 
        "cancellation" in text_lower or 
        "annul" in text_lower or 
        "annuler" in text_lower or 
        "annulation" in text_lower
    ):
        return "cancel"

    # ========================================================
    # RESCHEDULE
    # ========================================================

    if (
        "reschedule" in text_lower or 
        "reprogramm" in text_lower or 
        "reporter" in text_lower or 
        "déplacer" in text_lower or 
        "changer la date" in text_lower or
        "changer l'heure" in text_lower
    ):
        return "reschedule"

    # ========================================================
    # CHECK
    # ========================================================

    if (
        "check appointment" in text_lower
        or "appointment details" in text_lower
        or "appointment status" in text_lower
        or "vérifier" in text_lower
        or "consulter mon rendez-vous" in text_lower
        or "détails de mon rendez-vous" in text_lower
        or "mon rendez-vous" in text_lower
    ):
        return "check"

    # ========================================================
    # BOOK
    # ========================================================

    if (
        "book an appointment" in text_lower
        or "book appointment" in text_lower
        or "book a appointment" in text_lower
        or "make an appointment" in text_lower
        or "make appointment" in text_lower
        or "schedule an appointment" in text_lower
        or "schedule appointment" in text_lower
        or "want to book" in text_lower
        or "want to schedule" in text_lower
        or "need an appointment" in text_lower
        or "need appointment" in text_lower
        or "prendre rendez-vous" in text_lower
        or "prendre un rendez-vous" in text_lower
        or "nouveau rendez-vous" in text_lower
        or "réserver" in text_lower
        or "reservation" in text_lower
        or "réservation" in text_lower
    ):
        return "book"

    return None

