import json
from pathlib import Path
from typing import List, Dict, Any

import numpy as np
from openai import OpenAI

from src.config import (
    OPENAI_API_KEY,
    OPENAI_BASE_URL,
    EMBEDDING_MODEL,
    KNOWLEDGE_CHUNKS_PATH,
    PROCESSED_DATA_DIR,
)


EMBEDDINGS_PATH = PROCESSED_DATA_DIR / "embeddings.json"


class VectorStore:
    """
    Simple local vector store for the HealthConnect RAG prototype.

    The implementation:
    1. Loads knowledge chunks.
    2. Generates embeddings using the configured embedding model.
    3. Stores embeddings locally.
    4. Performs cosine-similarity search.
    """

    def __init__(self):
        self.client = OpenAI(
            api_key=OPENAI_API_KEY,
            base_url=OPENAI_BASE_URL,
        )

        self.documents: List[Dict[str, Any]] = []
        self.embeddings: List[List[float]] = []

    # --------------------------------------------------------
    # Load knowledge chunks
    # --------------------------------------------------------

    def load_documents(self):
        if not Path(KNOWLEDGE_CHUNKS_PATH).exists():
            raise FileNotFoundError(
                f"Knowledge chunks not found: {KNOWLEDGE_CHUNKS_PATH}"
            )

        with open(KNOWLEDGE_CHUNKS_PATH, "r", encoding="utf-8") as f:
            self.documents = json.load(f)

        if not isinstance(self.documents, list):
            raise ValueError(
                "knowledge_chunks.json must contain a list of documents."
            )

        print(
            f"Loaded {len(self.documents)} knowledge chunks."
        )

    # --------------------------------------------------------
    # Create embeddings
    # --------------------------------------------------------

    def create_embeddings(self, force: bool = False):
        """
        Generate embeddings for all knowledge chunks.

        If embeddings already exist, they are reused unless
        force=True.
        """

        if not self.documents:
            self.load_documents()

        if EMBEDDINGS_PATH.exists() and not force:
            print("Existing embeddings found. Loading them.")
            self.load_embeddings()
            return

        print(
            f"Creating embeddings using {EMBEDDING_MODEL}..."
        )

        texts = [
            document["text"]
            for document in self.documents
        ]

        response = self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=texts,
        )

        self.embeddings = [
            item.embedding
            for item in response.data
        ]

        records = []

        for document, embedding in zip(
            self.documents,
            self.embeddings
        ):
            records.append(
                {
                    "chunk_id": document["chunk_id"],
                    "embedding": embedding,
                }
            )

        with open(
            EMBEDDINGS_PATH,
            "w",
            encoding="utf-8"
        ) as f:
            json.dump(records, f)

        print(
            f"Embeddings created for {len(self.embeddings)} chunks."
        )

    # --------------------------------------------------------
    # Load embeddings
    # --------------------------------------------------------

    def load_embeddings(self):
        if not EMBEDDINGS_PATH.exists():
            raise FileNotFoundError(
                f"Embeddings file not found: {EMBEDDINGS_PATH}"
            )

        with open(
            EMBEDDINGS_PATH,
            "r",
            encoding="utf-8"
        ) as f:
            records = json.load(f)

        embedding_map = {
            record["chunk_id"]: record["embedding"]
            for record in records
        }

        self.embeddings = [
            embedding_map[document["chunk_id"]]
            for document in self.documents
        ]

        print(
            f"Loaded {len(self.embeddings)} embeddings."
        )

    # --------------------------------------------------------
    # Embed query
    # --------------------------------------------------------

    def embed_query(self, query: str) -> List[float]:
        response = self.client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=query,
        )

        return response.data[0].embedding

    # --------------------------------------------------------
    # Cosine similarity
    # --------------------------------------------------------

    @staticmethod
    def cosine_similarity(
        vector_a: List[float],
        vector_b: List[float],
    ) -> float:

        a = np.array(vector_a)
        b = np.array(vector_b)

        denominator = (
            np.linalg.norm(a) * np.linalg.norm(b)
        )

        if denominator == 0:
            return 0.0

        return float(
            np.dot(a, b) / denominator
        )

    # --------------------------------------------------------
    # Search
    # --------------------------------------------------------

    def search(
        self,
        query: str,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:

        if not self.documents:
            self.load_documents()

        if not self.embeddings:
            self.create_embeddings()

        query_embedding = self.embed_query(query)

        scored_documents = []

        for document, embedding in zip(
            self.documents,
            self.embeddings
        ):
            score = self.cosine_similarity(
                query_embedding,
                embedding
            )

            scored_documents.append(
                {
                    "chunk_id": document["chunk_id"],
                    "source": document["source"],
                    "text": document["text"],
                    "score": score,
                }
            )

        scored_documents.sort(
            key=lambda item: item["score"],
            reverse=True,
        )

        return scored_documents[:top_k]
