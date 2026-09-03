# HealthConnect AI 🩺

HealthConnect is an AI-powered healthcare assistant designed to help patients with clinic information and administrative tasks, such as managing appointments. 

It leverages **Retrieval-Augmented Generation (RAG)** to provide accurate information based on a clinic's knowledge base and includes built-in safety guardrails to ensure the AI does not provide medical diagnoses or treatment advice.

## 🌟 Features

- **Clinic Information (RAG)**: Answers questions based on a local knowledge base (`.docx` documents) using vector embeddings and cosine similarity search.
- **Appointment Management**: Capable of checking, cancelling, and rescheduling appointments (e.g., using reference `HC-1001`).
- **Safety Guardrails**: Detects and escalates medical emergencies, diagnosis requests, and medication inquiries to human staff.
- **Dual Interface**: Offers a beautiful Web UI built with Streamlit and a Command-Line Interface (CLI).

## 🚀 Getting Started

### 1. Prerequisites

Ensure you have Python 3.8+ installed.

### 2. Installation

Clone the repository and install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configuration

Create a `.env` file in the root of the project by copying the provided example:

```bash
cp .env.example .env
```

Open the `.env` file and set your `OPENAI_API_KEY`. By default, the app is configured to use OpenRouter, but you can change the `OPENAI_BASE_URL` and `OPENAI_MODEL` to use OpenAI or any compatible provider.

### 4. Running the Application

You can run the assistant in two ways:

**Option A: Web Interface (Recommended)**
Start the Streamlit application:
```bash
streamlit run app.py
```

**Option B: CLI Interface**
Run the terminal-based assistant:
```bash
python -m src.main
```

## 📂 Project Structure

- `app.py`: Streamlit Web Application.
- `src/main.py`: Command-Line Interface.
- `src/agent/`: Core assistant logic, LLM interaction, and intent routing.
- `src/rag/`: Vector store, document ingestion, and retriever.
- `src/appointments/`: Appointment management and mock database.
- `src/safety/`: Guardrails to prevent medical advice and handle escalations.
- `data/`: Contains the raw knowledge base, processed chunks, embeddings, and the appointment database.
- `tests/`: Unit tests for various components.

## ⚠️ Disclaimer

This assistant provides general information and administrative support. It does not diagnose medical conditions, provide treatment advice, or replace emergency medical services.
