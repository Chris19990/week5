import os
from pathlib import Path

from dotenv import load_dotenv

# ============================================================
# Environment
# ============================================================

load_dotenv()

# ============================================================
# Project paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
APPOINTMENTS_DIR = BASE_DIR / "data" / "appointments"

KNOWLEDGE_BASE_PATH = (
    RAW_DATA_DIR / "HealthConnect_Clinic_Knowledge_Base.docx"
)

KNOWLEDGE_CHUNKS_PATH = (
    PROCESSED_DATA_DIR / "knowledge_chunks.json"
)

EMBEDDINGS_PATH = (
    PROCESSED_DATA_DIR / "embeddings.json"
)

APPOINTMENTS_DB_PATH = (
    APPOINTMENTS_DIR / "appointments.db"
)

# ============================================================
# OpenRouter / OpenAI-compatible API
# ============================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

OPENAI_BASE_URL = os.getenv(
    "OPENAI_BASE_URL",
    "https://openrouter.ai/api/v1"
).strip()

OPENAI_MODEL = os.getenv(
    "OPENAI_MODEL",
    "openrouter/free"
).strip()

# ============================================================
# Embeddings
# ============================================================

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "text-embedding-3-small"
).strip()

# ============================================================
# RAG
# ============================================================

TOP_K = int(os.getenv("TOP_K", "3"))

# Minimum cosine similarity required for a retrieved chunk.
# This prevents weakly related knowledge from being passed
# to the LLM as if it were relevant.
RAG_MIN_SCORE = float(
    os.getenv("RAG_MIN_SCORE", "0.40")
)

# ============================================================
# LLM generation
# ============================================================

TEMPERATURE = float(
    os.getenv("TEMPERATURE", "0.1")
)

MAX_TOKENS = int(
    os.getenv("MAX_TOKENS", "500")
)

# ============================================================
# Fallback models
# ============================================================

OPENAI_FALLBACK_MODELS = [
    model.strip()
    for model in os.getenv(
        "OPENAI_FALLBACK_MODELS",
        ""
    ).split(",")
    if model.strip()
]

# ============================================================
# Create required directories
# ============================================================

RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
APPOINTMENTS_DIR.mkdir(parents=True, exist_ok=True)
