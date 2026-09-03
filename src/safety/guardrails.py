from src.agent.router import classify_intent


def safety_check(user_message):

    intent = classify_intent(user_message)

    if intent == "emergency":

        return {
            "allowed": False,
            "category": "emergency",
        }

    if intent == "medical":

        return {
            "allowed": False,
            "category": "medical",
        }

    return {
        "allowed": True,
        "category": "administrative",
    }
