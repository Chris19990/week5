from src.rag.vector_store import VectorStore
from src.config import TOP_K, RAG_MIN_SCORE


class Retriever:
    """
    Retrieval layer for the HealthConnect RAG system.
    """

    def __init__(self, top_k=TOP_K):
        self.top_k = top_k

        self.vector_store = VectorStore()

        self.vector_store.load_documents()

        # Create embeddings only when necessary.
        self.vector_store.create_embeddings()

    def retrieve(self, query, top_k=None):
        """
        Retrieve relevant knowledge chunks.
        """

        if not query or not query.strip():
            return []

        k = top_k or self.top_k

        results = self.vector_store.search(
            query,
            top_k=k
        )

        # Keep only reasonably relevant results.
        filtered_results = [
            result
            for result in results
            if result.get("score", 0) >= RAG_MIN_SCORE
        ]

        return filtered_results

    def get_context(self, query, top_k=None):
        """
        Build the context passed to the LLM.
        """

        results = self.retrieve(
            query,
            top_k=top_k
        )

        if not results:
            return ""

        context_parts = []

        for result in results:
            context_parts.append(
                f"[Source: {result['source']} | "
                f"Chunk: {result['chunk_id']} | "
                f"Score: {result['score']:.4f}]\n"
                f"{result['text']}"
            )

        return "\n\n---\n\n".join(context_parts)
