import json
import re
from pathlib import Path

from docx import Document

from src.config import KNOWLEDGE_BASE_PATH, KNOWLEDGE_CHUNKS_PATH


def extract_text_from_docx(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(
            f"Knowledge Base not found: {path}"
        )

    document = Document(path)

    paragraphs = [
        paragraph.text.strip()
        for paragraph in document.paragraphs
        if paragraph.text.strip()
    ]

    return "\n".join(paragraphs)


def clean_text(text: str) -> str:
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def chunk_text(text: str, max_chars: int = 1200) -> list[str]:
    paragraphs = text.split("\n")
    chunks = []
    current = ""

    for paragraph in paragraphs:
        paragraph = paragraph.strip()

        if not paragraph:
            continue

        candidate = (
            f"{current}\n{paragraph}"
            if current
            else paragraph
        )

        if len(candidate) <= max_chars:
            current = candidate
        else:
            if current:
                chunks.append(current.strip())

            current = paragraph

    if current:
        chunks.append(current.strip())

    return chunks


def build_knowledge_chunks() -> list[dict]:
    raw_text = extract_text_from_docx(KNOWLEDGE_BASE_PATH)
    cleaned_text = clean_text(raw_text)

    chunks = chunk_text(cleaned_text)

    records = []

    for index, chunk in enumerate(chunks):
        records.append(
            {
                "chunk_id": f"kb_{index + 1:04d}",
                "source": KNOWLEDGE_BASE_PATH.name,
                "text": chunk,
            }
        )

    KNOWLEDGE_CHUNKS_PATH.write_text(
        json.dumps(
            records,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    return records


if __name__ == "__main__":
    records = build_knowledge_chunks()

    print(
        f"Knowledge Base processed successfully: "
        f"{len(records)} chunks created."
    )
