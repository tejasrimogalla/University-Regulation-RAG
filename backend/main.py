from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from backend.config import settings
from backend.utils.logging_config import logger
from backend.api.chat import router as chat_router
from backend.api.documents import router as documents_router
from backend.embeddings.model import get_embedding_service
from backend.vectorstore.faiss_store import get_vector_store
from backend.llm.nvidia_client import get_nvidia_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown tasks.
    Pre-loads the embedding model and loads existing FAISS index if present.
    """
    logger.info("Initializing University Regulation RAG Assistant backend...")
    settings.ensure_directories()

    # Pre-load embedding model singleton once
    try:
        get_embedding_service()
    except Exception as e:
        logger.error(f"Failed to pre-load embedding model: {e}")

    # Load FAISS index if present
    try:
        vs = get_vector_store()
        if vs.index is not None:
            logger.info(f"Loaded existing index with {vs.index.ntotal} vectors.")
        else:
            logger.info("No index currently loaded. Awaiting document upload and rebuild.")
    except Exception as e:
        logger.error(f"Error checking FAISS index: {e}")

    yield

    logger.info("Shutting down University Regulation RAG Assistant backend.")

app = FastAPI(
    title="University Regulation RAG Assistant API",
    description="Production RAG API for university regulations, guidelines, and handbooks using FAISS and NVIDIA API.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for React/Vite development server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows Vite dev server & production builds
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(chat_router)
app.include_router(documents_router)

@app.get("/health", tags=["system"])
def health_check():
    """
    System health check.
    Reports NVIDIA configuration state and index metrics without exposing secrets.
    """
    nvidia_client = get_nvidia_client()
    vector_store = get_vector_store()
    stats = vector_store.get_stats()

    return {
        "status": "ok",
        "nvidia_configured": nvidia_client.is_configured(),
        "nvidia_model": settings.NVIDIA_MODEL,
        "index_loaded": stats["loaded"],
        "indexed_chunks": stats["total_chunks"],
        "unique_documents": stats["unique_documents"]
    }

# Mount frontend production build if it exists
frontend_dist = settings.BASE_DIR / "frontend" / "dist"
if frontend_dist.exists() and frontend_dist.is_dir():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")
