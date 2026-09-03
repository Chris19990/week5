def escalation_response(category):

    if category == "emergency":

        return (
            "This assistant does not provide emergency medical support. "
            "If you believe you are experiencing a medical emergency, "
            "seek immediate help from the appropriate emergency service "
            "or the nearest emergency facility."
        )

    if category in [
        "medical",
        "diagnosis",
        "medication",
    ]:

        return (
            "I’m unable to diagnose medical conditions or provide "
            "medical, treatment, or medication advice. "
            "Please consult a qualified healthcare professional."
        )

    return (
        "I don't have enough approved information to answer that request. "
        "Please contact HealthConnect Clinic reception for assistance."
    )
