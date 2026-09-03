from src.agent.assistant import HealthConnectAssistant
from src.appointments.database import (
    initialize_database,
    seed_demo_data,
)


def main():
    print("=" * 60)
    print("HealthConnect Healthcare Information Assistant")
    print("=" * 60)
    print("Type 'exit' or 'quit' to end the conversation.")
    print()

    initialize_database()
    seed_demo_data()

    assistant = HealthConnectAssistant()

    while True:

        try:
            user_message = input("You: ").strip()

        except (KeyboardInterrupt, EOFError):
            print("\nAssistant: Goodbye.")
            break

        if user_message.lower() in [
            "exit",
            "quit",
        ]:
            print("Assistant: Goodbye.")
            break

        if not user_message:
            continue

        try:
            response = assistant.answer(
                user_message
            )

            print()
            print(
                f"Assistant: {response}"
            )
            print()

        except Exception as error:
            print(
                "Assistant: An unexpected error occurred."
            )

            print(
                f"[Technical details: {error}]"
            )


if __name__ == "__main__":
    main()
