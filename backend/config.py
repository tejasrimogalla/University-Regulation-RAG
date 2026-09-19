import os
from pathlib import Path
from dotenv import load_dotenv

# Load backend/.env
BACKEND_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = BACKEND_DIR.parent
ENV_PATH = BACKEND_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(dotenv_path=ENV_PATH)
else:
    load_dotenv()

import sys
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

class Settings:
    # Directories
    BASE_DIR: Path = PROJECT_ROOT
    DATA_DIR: Path = PROJECT_ROOT / "data"
    DOCUMENTS_DIR: Path = DATA_DIR / "documents"
    INDEX_DIR: Path = DATA_DIR / "index"
    FAISS_INDEX_PATH: Path = INDEX_DIR / "index.faiss"
    METADATA_PATH: Path = INDEX_DIR / "metadata.json"

    # NVIDIA API
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "").strip()
    NVIDIA_BASE_URL: str = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1").rstrip("/")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "meta/llama-3.2-11b-vision-instruct").strip()

    # Embeddings & RAG
    EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2").strip()
    TOP_K: int = int(os.getenv("TOP_K", "5"))
    MIN_SIMILARITY: float = float(os.getenv("MIN_SIMILARITY", "0.35"))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "1000"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "200"))

    # Security / Allowed Extensions
    ALLOWED_EXTENSIONS: set = {".pdf"}

    def ensure_directories(self):
        self.DOCUMENTS_DIR.mkdir(parents=True, exist_ok=True)
        self.INDEX_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
settings.ensure_directories()
