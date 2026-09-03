from src.rag.ingest import chunk_text


def test_chunking():
    text = (
        "HealthConnect Clinic is open Monday to Friday."
        "\n"
        "Appointments can be requested through an "
        "approved booking channel."
    )

    chunks = chunk_text(
        text,
        max_chars=200,
    )

    assert len(chunks) >= 1
    assert "HealthConnect Clinic" in chunks[0]
