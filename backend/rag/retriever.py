import re
from typing import List, Dict, Any, Optional
from backend.config import settings
from backend.embeddings.model import get_embedding_service
from backend.vectorstore.faiss_store import get_vector_store
from backend.utils.logging_config import logger

class RegulationRetriever:
    """
    Handles query preprocessing, vector embedding, FAISS similarity search,
    score filtering, and deduplication of retrieved university regulation chunks.
    """

    def __init__(
        self,
        top_k: int = settings.TOP_K,
        min_similarity: float = settings.MIN_SIMILARITY
    ):
        self.top_k = top_k
        self.min_similarity = min_similarity
        self.embedding_service = get_embedding_service()
        self.vector_store = get_vector_store()

    def clean_query(self, query: str) -> str:
        """Cleans and normalizes the user question."""
        if not query:
            return ""
        # Strip excessive whitespace
        cleaned = re.sub(r"\s+", " ", query).strip()
        return cleaned

    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        min_similarity: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes similarity search on FAISS and applies relevance threshold.
        Returns list of relevant chunks formatted for RAG.
        """
        k = top_k if top_k is not None else self.top_k
        threshold = min_similarity if min_similarity is not None else self.min_similarity

        cleaned_query = self.clean_query(query)
        if not cleaned_query:
            logger.warning("Empty query passed to retriever.")
            return []

        # Check if vector store is ready
        if self.vector_store.index is None or self.vector_store.index.ntotal == 0:
            logger.warning("Retrieval attempted on empty or uninitialized FAISS index.")
            return []

        # Generate query vector
        query_vector = self.embedding_service.encode_query(cleaned_query)

        # FAISS search
        raw_results = self.vector_store.search(query_vector, top_k=k)
        logger.info(f"FAISS retrieved {len(raw_results)} candidates for query: '{cleaned_query}'")

        # Filter by minimum similarity threshold
        filtered_results: List[Dict[str, Any]] = []
        seen_snippets = set()

        for chunk in raw_results:
            score = chunk.get("score", 0.0)
            logger.debug(
                f"Candidate: {chunk.get('source')} (p. {chunk.get('page')}) - Score: {score:.4f} "
                f"(Threshold: {threshold})"
            )

            if score < threshold:
                logger.info(
                    f"Chunk from '{chunk.get('source')}' (page {chunk.get('page')}) dropped: "
                    f"score {score:.4f} < {threshold}"
                )
                continue

            # Deduplicate near-identical text snippets
            snippet_key = (chunk.get("source"), chunk.get("page"), chunk.get("text", "")[:100])
            if snippet_key in seen_snippets:
                continue
            seen_snippets.add(snippet_key)

            filtered_results.append({
                "document": chunk.get("source", "Unknown Document"),
                "page": chunk.get("page", 1),
                "score": round(score, 4),
                "text": chunk.get("text", ""),
                "chunk_id": chunk.get("chunk_id", 0)
            })

        logger.info(f"Retriever retained {len(filtered_results)} chunks above similarity {threshold}.")
        return filtered_results
