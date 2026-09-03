from openai import OpenAI
import re

from src.config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    OPENAI_MODEL,
    OPENAI_FALLBACK_MODELS,
    TEMPERATURE,
    MAX_TOKENS,
)

from src.rag.retriever import Retriever

from src.appointments.tools import (
    tool_check_appointment,
    tool_cancel_appointment,
    tool_reschedule_appointment,
    tool_book_appointment,
)

from src.agent.router import (
    classify_intent,
    classify_appointment_action,
)

from src.safety.guardrails import safety_check
from src.safety.escalation import escalation_response
from src.agent.prompts import SYSTEM_PROMPT


class HealthConnectAssistant:

    def __init__(self):

        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
        )

        self.retriever = Retriever()

        # ====================================================
        # BOOKING CONVERSATION STATE
        # ====================================================

        self.booking_state = {
            "active": False,
            "clinic_name": None,
            "service_name": None,
            "appointment_date": None,
            "appointment_time": None,
            "patient_name": None,
            "patient_id": None,
        }

        self.manage_state = {
            "active": False,
            "action": None,
            "appointment_id": None,
        }

    # ========================================================
    # LLM CALL
    # ========================================================

    def _generate_response(self, user_message, context):

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": (
                    "Use ONLY the approved HealthConnect knowledge "
                    "provided in the context below.\n\n"
                    "APPROVED CONTEXT:\n"
                    f"{context}\n\n"
                    "USER QUESTION:\n"
                    f"{user_message}"
                ),
            },
        ]

        models = [OPENAI_MODEL] + OPENAI_FALLBACK_MODELS

        last_error = None

        for model in models:

            try:

                print(f"[LLM] Trying model: {model}")

                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=TEMPERATURE,
                    max_tokens=MAX_TOKENS,
                )

                answer = response.choices[0].message.content

                if answer:
                    return answer.strip()

            except Exception as error:

                last_error = error

                print(
                    f"[LLM] Model failed: "
                    f"{model} -> {type(error).__name__}"
                )

        return (
            "I'm sorry, but the AI response service is temporarily "
            "unavailable. Please contact HealthConnect Clinic reception "
            "for assistance."
        )

    # ========================================================
    # RESET BOOKING STATE
    # ========================================================

    def _reset_booking_state(self):

        self.booking_state = {
            "active": False,
            "clinic_name": None,
            "service_name": None,
            "appointment_date": None,
            "appointment_time": None,
            "patient_name": None,
            "patient_id": None,
        }

    def _reset_manage_state(self):
        self.manage_state = {
            "active": False,
            "action": None,
            "appointment_id": None,
        }

    # ========================================================
    # BOOKING CONVERSATION
    # ========================================================

    def _handle_booking_conversation(self, user_message):

        state = self.booking_state
        message = user_message.strip()
        message_lower = message.lower()
        
        is_initial_booking_message = not state["active"]

        if not state["active"]:
            state["active"] = True

        # ====================================================
        # EXTRACTION PHASE
        # ====================================================

        extracted_something = False

        if state["clinic_name"] is None:
            if "central" in message_lower:
                state["clinic_name"] = "Central Clinic"
                extracted_something = True
            elif "lakeside" in message_lower:
                state["clinic_name"] = "Lakeside Clinic"
                extracted_something = True

        if state["service_name"] is None:
            if "general" in message_lower or "générale" in message_lower:
                state["service_name"] = "General outpatient consultation"
                extracted_something = True
            elif "follow" in message_lower or "suivi" in message_lower:
                state["service_name"] = "Follow-up consultation"
                extracted_something = True

        if state["appointment_date"] is None:
            date_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", message)
            if date_match:
                state["appointment_date"] = date_match.group(1)
                extracted_something = True

        if state["appointment_time"] is None:
            time_match = re.search(r"\b([01]?\d|2[0-3])\s*[:h]\s*([0-5]\d)\b", message_lower)
            if time_match:
                state["appointment_time"] = f"{time_match.group(1).zfill(2)}:{time_match.group(2)}"
                extracted_something = True

        # ====================================================
        # VALIDATION & PROMPTING PHASE
        # ====================================================

        if state["clinic_name"] is None:
            prefix = "Sure. I can help you book an appointment.\n\n" if is_initial_booking_message else ""
            return (
                f"{prefix}Which clinic would you prefer?\n"
                "- Central Clinic\n"
                "- Lakeside Clinic"
            )

        if state["service_name"] is None:
            return (
                "Which type of appointment would you like?\n\n"
                "- General outpatient consultation\n"
                "- Follow-up consultation"
            )

        if state["appointment_date"] is None:
            return (
                "What date would you like for your appointment?\n\n"
                "Please provide the date in the format YYYY-MM-DD."
            )

        from src.appointments.availability import (
            get_available_slots,
            is_slot_available,
        )

        if state["appointment_time"] is None:
            result = get_available_slots(
                clinic_name=state["clinic_name"],
                appointment_date=state["appointment_date"],
            )

            if not result["success"]:
                state["appointment_date"] = None
                return result["message"]

            slots = result["slots"]

            if not slots:
                state["appointment_date"] = None
                return (
                    "There are no available appointment times "
                    "on that date. Please choose another date."
                )

            slots_text = "\n".join(f"- {slot}" for slot in slots)

            return (
                f"Available times at {state['clinic_name']} "
                f"on {state['appointment_date']}:\n\n"
                f"{slots_text}\n\n"
                "Please choose one of these times."
            )

        result = is_slot_available(
            clinic_name=state["clinic_name"],
            appointment_date=state["appointment_date"],
            appointment_time=state["appointment_time"],
        )

        if not result["available"]:
            state["appointment_time"] = None
            return (
                f"That time is not available. "
                f"{result['reason']}\n\n"
                "Please choose another available time."
            )

        if state["patient_name"] is None:

            if is_initial_booking_message or extracted_something:
                return "What is the patient's full name?"

            if len(message) < 2:
                return "Please provide the patient's full name."

            state["patient_name"] = message
            
            import uuid
            state["patient_id"] = "P-" + uuid.uuid4().hex[:6].upper()

            return (
                "Please confirm your appointment:\n\n"
                f"Clinic: {state['clinic_name']}\n"
                f"Service: {state['service_name']}\n"
                f"Date: {state['appointment_date']}\n"
                f"Time: {state['appointment_time']}\n"
                f"Patient: {state['patient_name']}\n\n"
                "Would you like me to confirm this appointment?"
            )

        if message.lower() in [
            "yes",
            "y",
            "yes please",
            "confirm",
            "confirmed",
            "oui",
            "je confirme",
            "ok",
        ]:

            result = tool_book_appointment(
                patient_id=state["patient_id"],
                patient_name=state["patient_name"],
                clinic_name=state["clinic_name"],
                service_name=state["service_name"],
                appointment_date=state["appointment_date"],
                appointment_time=state["appointment_time"],
            )

            if not result["success"]:
                return result["message"]

            appointment_id = result["appointment_id"]
            clinic = result.get("clinic", state["clinic_name"])
            service = result.get("service", state["service_name"])
            appointment_date = result.get("date", state["appointment_date"])
            appointment_time = result.get("time", state["appointment_time"])

            self._reset_booking_state()

            return (
                "Your appointment has been booked successfully.\n\n"
                f"Appointment reference: {appointment_id}\n"
                f"Clinic: {clinic}\n"
                f"Service: {service}\n"
                f"Date: {appointment_date}\n"
                f"Time: {appointment_time}"
            )

        return (
            "Please answer yes to confirm the appointment, "
            "or tell me if you would like to change something."
        )

    # ========================================================
    # APPOINTMENT ACTIONS
    # ========================================================

    def _handle_manage_conversation(self, user_message):

        state = self.manage_state
        message = user_message.strip()
        message_lower = message.lower()

        if state["appointment_id"] is None:
            appointment_match = re.search(r"\bHC-\d+\b", message, re.IGNORECASE)
            if appointment_match:
                state["appointment_id"] = appointment_match.group(0).upper()
            else:
                return "Veuillez indiquer la référence de votre rendez-vous, par exemple HC-1001."

        action = state["action"]
        appointment_id = state["appointment_id"]

        # ====================================================
        # CHECK
        # ====================================================
        if action == "check":
            self._reset_manage_state()
            appointment = tool_check_appointment(appointment_id)
            if appointment is None:
                return (
                    f"Je n'ai pas pu trouver le rendez-vous {appointment_id}. "
                    "Veuillez vérifier votre référence ou contacter la réception."
                )
            return (
                f"Rendez-vous {appointment_id}:\n"
                f"- Clinique: {appointment['clinic_location']}\n"
                f"- Service: {appointment['service']}\n"
                f"- Date: {appointment['appointment_date']}\n"
                f"- Heure: {appointment['appointment_time']}\n"
                f"- Statut: {appointment['status']}"
            )

        # ====================================================
        # CANCEL
        # ====================================================
        if action == "cancel":
            self._reset_manage_state()
            result = tool_cancel_appointment(appointment_id)
            if not result["success"]:
                return result["message"]
            return f"Le rendez-vous {appointment_id} a été annulé avec succès."

        # ====================================================
        # RESCHEDULE
        # ====================================================
        if action == "reschedule":
            date_match = re.search(r"\b(20\d{2}-\d{2}-\d{2})\b", message)
            time_match = re.search(r"\b([01]?\d|2[0-3])\s*[:h]\s*([0-5]\d)\b", message_lower)

            if not date_match or not time_match:
                return (
                    "Pour reporter votre rendez-vous, veuillez fournir "
                    "la nouvelle date et heure (ex: 2026-10-15 14:00)."
                )

            new_date = date_match.group(1)
            new_time = f"{time_match.group(1).zfill(2)}:{time_match.group(2)}"
            
            self._reset_manage_state()
            result = tool_reschedule_appointment(appointment_id, new_date, new_time)

            if not result["success"]:
                return result["message"]

            return (
                f"Le rendez-vous {appointment_id} a été "
                f"reporté au {new_date} à {new_time}."
            )

        self._reset_manage_state()
        return "I couldn't process that appointment request."

    # ========================================================
    # MAIN ASSISTANT
    # ========================================================

    def answer(self, user_message):

        if not user_message or not user_message.strip():

            return (
                "Please enter a question so I can help you."
            )

        user_message = user_message.strip()

        # ====================================================
        # SAFETY FIRST
        # ====================================================

        safety_result = safety_check(user_message)

        if not safety_result["allowed"]:

            return escalation_response(
                safety_result["category"]
            )

        # ====================================================
        # ACTIVE BOOKING CONVERSATION
        # ====================================================

        if self.booking_state["active"]:

            return self._handle_booking_conversation(
                user_message
            )

        # ====================================================
        # ACTIVE MANAGE CONVERSATION
        # ====================================================

        if self.manage_state["active"]:
            return self._handle_manage_conversation(user_message)

        # ====================================================
        # INTENT
        # ====================================================

        intent = classify_intent(user_message)

        # ====================================================
        # APPOINTMENT ACTION
        # ====================================================

        appointment_action = classify_appointment_action(
            user_message
        )

        if appointment_action == "book":

            self.booking_state["active"] = True

            return self._handle_booking_conversation(
                user_message
            )

        if appointment_action:
            self.manage_state["active"] = True
            self.manage_state["action"] = appointment_action

            return self._handle_manage_conversation(
                user_message
            )

        # ====================================================
        # HIGH-RISK INTENTS
        # ====================================================

        if intent in [
            "medical",
            "diagnosis",
            "medication",
            "emergency",
        ]:

            return escalation_response(intent)

        # ====================================================
        # RAG
        # ====================================================

        try:

            results = self.retriever.retrieve(
                user_message
            )

        except Exception as error:

            print(
                f"[RAG ERROR] {type(error).__name__}: {error}"
            )

            return (
                "I'm sorry, I couldn't access the clinic information "
                "right now. Please contact HealthConnect Clinic reception."
            )

        if not results:

            return (
                "I don't have enough approved information to answer "
                "that question. Please contact HealthConnect Clinic "
                "reception for assistance."
            )

        # ====================================================
        # BUILD CONTEXT
        # ====================================================

        context_parts = []

        for result in results:

            context_parts.append(
                "[Source: "
                f"{result['chunk_id']}"
                " | "
                f"Score: {result['score']:.4f}"
                "]\n"
                f"{result['text']}"
            )

        context = "\n\n".join(
            context_parts
        )

        # ====================================================
        # GENERATE
        # ====================================================

        return self._generate_response(
            user_message,
            context,
        )
