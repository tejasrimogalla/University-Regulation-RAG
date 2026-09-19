import json
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import faiss
import numpy as np
from backend.config import settings
from backend.utils.logging_config import logger

class FAISSVectorStore:
    """
    Manages FAISS IndexFlatIP (cosine similarity over normalized embeddings)
    alongside a JSON metadata store for mapping vectors to document source, page,
    and text.
    """

    def __init__(
        self,
        index_path: Path = settings.FAISS_INDEX_PATH,
        metadata_path: Path = settings.METADATA_PATH,
        dimension: int = 384
    ):
        self.index_path = index_path
        self.metadata_path = metadata_path
        self.dimension = dimension
        self.index: Optional[faiss.IndexFlatIP] = None
        self.metadata: List[Dict[str, Any]] = []

    def load_index(self) -> bool:
        """
        Loads the FAISS index and metadata from disk if they exist.
        Returns True if successfully loaded, False otherwise.
        """
        if not self.index_path.exists() or not self.metadata_path.exists():
            logger.info("No existing FAISS index or metadata found on disk.")
            self.index = None
            self.metadata = []
            return False

        try:
            logger.info(f"Loading FAISS index from {self.index_path}...")
            self.index = faiss.read_index(str(self.index_path))

            with open(self.metadata_path, "r", encoding="utf-8") as f:
                self.metadata = json.load(f)

            if self.index.ntotal != len(self.metadata):
                logger.warning(
                    f"Index size ({self.index.ntotal}) does not match metadata count ({len(self.metadata)}). "
                    "Rebuild recommended."
                )

            logger.info(f"FAISS index loaded successfully with {self.index.ntotal} vectors.")
            return True
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {str(e)}")
            self.index = None
            self.metadata = []
            return False

    def save_index(self) -> None:
        """
        Persists the current FAISS index and metadata to disk.
        """
        if self.index is None:
            raise ValueError("Cannot save an uninitialized FAISS index.")

        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        self.metadata_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            faiss.write_index(self.index, str(self.index_path))
            with open(self.metadata_path, "w", encoding="utf-8") as f:
                json.dump(self.metadata, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved FAISS index ({self.index.ntotal} vectors) to {self.index_path}")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {str(e)}")
            raise

    def build_index(self, chunks: List[Dict[str, Any]], embeddings: np.ndarray) -> None:
        """
        Builds a new FAISS index from document chunks and their normalized embeddings.
        Overwrites existing in-memory index and saves to disk.
        """
        if len(chunks) == 0 or embeddings.shape[0] == 0:
            self.clear_index()
            return

        dim = embeddings.shape[1]
        self.dimension = dim

        # Create Flat Inner Product index for cosine similarity with normalized vectors
        new_index = faiss.IndexFlatIP(dim)
        new_index.add(embeddings)

        self.index = new_index
        self.metadata = chunks
        self.save_index()
        logger.info(f"FAISS index successfully built with {self.index.ntotal} vectors.")

    def search(self, query_vector: np.ndarray, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Performs inner product search on the normalized query vector.
        Returns list of results with metadata and similarity score.
        """
        if self.index is None or self.index.ntotal == 0:
            logger.warning("Search called on an empty or uninitialized FAISS index.")
            return []

        # Ensure 2D float32 shape
        if query_vector.ndim == 1:
            query_vector = np.expand_dims(query_vector, axis=0).astype(np.float32)

        k = min(top_k, self.index.ntotal)
        scores, indices = self.index.search(query_vector, k)

        results: List[Dict[str, Any]] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self.metadata):
                continue
            chunk_data = dict(self.metadata[idx])
            chunk_data["score"] = float(score)
            results.append(chunk_data)

        return results

    def clear_index(self) -> None:
        """
        Clears the in-memory index and removes persisted files.
        """
        self.index = None
        self.metadata = []
        if self.index_path.exists():
            try:
                self.index_path.unlink()
            except Exception as e:
                logger.warning(f"Could not delete index file {self.index_path}: {e}")
        if self.metadata_path.exists():
            try:
                self.metadata_path.unlink()
            except Exception as e:
                logger.warning(f"Could not delete metadata file {self.metadata_path}: {e}")
        logger.info("FAISS index and metadata cleared.")

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics about the current index."""
        is_loaded = self.index is not None and self.index.ntotal > 0
        unique_documents = set(m.get("source", "") for m in self.metadata if m.get("source"))
        return {
            "loaded": is_loaded,
            "total_chunks": self.index.ntotal if self.index else 0,
            "unique_documents": len(unique_documents),
            "document_names": sorted(list(unique_documents)),
            "dimension": self.dimension
        }

_vector_store: Optional[FAISSVectorStore] = None

def get_vector_store() -> FAISSVectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = FAISSVectorStore()
        _vector_store.load_index()
    return _vector_store
