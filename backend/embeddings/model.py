from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.config import settings
from backend.utils.logging_config import logger

class EmbeddingService:
    """
    Singleton service for generating normalized dense embeddings
    using sentence-transformers/all-MiniLM-L6-v2.
    Loaded once at application startup.
    """
    _instance: Optional["EmbeddingService"] = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(EmbeddingService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, model_name: str = settings.EMBEDDING_MODEL_NAME):
        if getattr(self, "_initialized", False):
            return
        logger.info(f"Loading embedding model: {model_name}...")
        try:
            self.model = SentenceTransformer(model_name)
            if hasattr(self.model, "get_embedding_dimension"):
                self.embedding_dimension = self.model.get_embedding_dimension()
            else:
                self.embedding_dimension = self.model.get_sentence_embedding_dimension()
            logger.info(f"Embedding model '{model_name}' loaded successfully (dimension: {self.embedding_dimension}).")
            self._initialized = True
        except Exception as e:
            logger.error(f"Failed to load embedding model '{model_name}': {str(e)}")
            raise RuntimeError(f"Could not initialize embedding model: {str(e)}") from e

    def encode_documents(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """
        Batch encodes a list of document chunk texts into normalized L2 float32 vectors.
        Normalized vectors enable inner product (IP) to be equivalent to cosine similarity.
        """
        if not texts:
            return np.empty((0, self.embedding_dimension), dtype=np.float32)

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embeddings.astype(np.float32)

    def encode_query(self, query: str) -> np.ndarray:
        """
        Encodes a single user query into a 1D normalized L2 float32 vector.
        """
        if not query or not query.strip():
            raise ValueError("Query string cannot be empty.")

        embedding = self.model.encode(
            [query.strip()],
            normalize_embeddings=True,
            convert_to_numpy=True
        )
        return embedding.astype(np.float32)[0]

_embedding_service: Optional[EmbeddingService] = None

def get_embedding_service() -> EmbeddingService:
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
