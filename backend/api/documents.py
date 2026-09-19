import re
import shutil
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import FileResponse
from backend.config import settings
from backend.ingestion.pdf_loader import PDFLoader
from backend.ingestion.chunker import IntelligentChunker
from backend.embeddings.model import get_embedding_service
from backend.vectorstore.faiss_store import get_vector_store
from backend.utils.logging_config import logger

router = APIRouter(prefix="", tags=["documents"])

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes user-provided filename to prevent path traversal and shell injection.
    Only allows alphanumeric characters, dashes, underscores, and dots.
    """
    base_name = Path(filename).name
    # Strip any directory separators or path traversal attempts
    cleaned = re.sub(r"[^a-zA-Z0-9_.-]", "_", base_name)
    # Remove leading dots or dashes
    cleaned = cleaned.lstrip(".-")
    if not cleaned or not cleaned.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid filename '{filename}'. Only valid .pdf files are accepted."
        )
    return cleaned

@router.get("/documents")
def list_documents() -> Dict[str, Any]:
    """
    Lists all PDF documents currently stored in data/documents/ along with size and metadata.
    """
    docs_dir = settings.DOCUMENTS_DIR
    vector_store = get_vector_store()
    indexed_doc_names = set(vector_store.get_stats().get("document_names", []))

    files = []
    for p in sorted(docs_dir.glob("*.pdf")):
        stat = p.stat()
        files.append({
            "filename": p.name,
            "size_bytes": stat.st_size,
            "size_kb": round(stat.st_size / 1024, 2),
            "indexed": p.name in indexed_doc_names,
            "modified_time": stat.st_mtime
        })

    return {
        "total_documents": len(files),
        "documents": files
    }

@router.post("/documents/upload")
async def upload_documents(files: List[UploadFile] = File(...)) -> Dict[str, Any]:
    """
    Uploads multiple PDF files. Rejects non-PDFs, sanitizes filenames,
    and stores them in data/documents/.
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for upload.")

    uploaded = []
    errors = []

    for file in files:
        original_name = file.filename or "unknown.pdf"
        # Strict extension validation
        if not original_name.lower().endswith(".pdf"):
            errors.append({
                "filename": original_name,
                "error": "Only PDF files (.pdf) are permitted."
            })
            continue

        try:
            safe_name = sanitize_filename(original_name)
            target_path = settings.DOCUMENTS_DIR / safe_name

            # Stream content to disk
            with open(target_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            uploaded.append({
                "original_name": original_name,
                "saved_as": safe_name,
                "size_bytes": target_path.stat().st_size
            })
            logger.info(f"Successfully uploaded and saved: {safe_name}")
        except HTTPException as he:
            errors.append({"filename": original_name, "error": he.detail})
        except Exception as e:
            logger.error(f"Failed to upload '{original_name}': {str(e)}")
            errors.append({"filename": original_name, "error": str(e)})

    return {
        "uploaded_count": len(uploaded),
        "uploaded_files": uploaded,
        "errors": errors
    }

@router.delete("/documents/{filename}")
def delete_document(filename: str) -> Dict[str, Any]:
    """
    Deletes a specific PDF document from data/documents/.
    """
    safe_name = sanitize_filename(filename)
    target_path = settings.DOCUMENTS_DIR / safe_name

    if not target_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{safe_name}' not found."
        )

    try:
        target_path.unlink()
        logger.info(f"Deleted document: {safe_name}")
        return {
            "success": True,
            "message": f"Document '{safe_name}' deleted. Please rebuild the index to reflect changes."
        }
    except Exception as e:
        logger.error(f"Error deleting file '{safe_name}': {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.get("/documents/{filename}")
def view_document(filename: str):
    """
    Streams the requested PDF file so the browser or frontend can display it.
    Supports browser #page=X navigation.
    """
    safe_name = sanitize_filename(filename)
    target_path = settings.DOCUMENTS_DIR / safe_name

    if not target_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document '{safe_name}' not found."
        )

    return FileResponse(
        path=target_path,
        media_type="application/pdf",
        filename=safe_name,
        content_disposition_type="inline"
    )

@router.post("/index/rebuild")
def rebuild_index() -> Dict[str, Any]:
    """
    Full pipeline:
    data/documents/*.pdf -> PyMuPDF page-by-page extraction -> text cleaning ->
    intelligent chunking -> sentence-transformers batch embeddings -> FAISS IndexFlatIP -> save metadata.json
    """
    pdf_files = list(settings.DOCUMENTS_DIR.glob("*.pdf"))
    if not pdf_files:
        # Clear existing index if no documents exist
        get_vector_store().clear_index()
        return {
            "success": True,
            "documents": 0,
            "pages": 0,
            "chunks": 0,
            "warnings": ["No PDF documents found in data/documents/ to index."]
        }

    all_chunks = []
    total_pages = 0
    warnings = []
    chunker = IntelligentChunker()

    current_chunk_id = 0
    for pdf_path in pdf_files:
        try:
            loader = PDFLoader(pdf_path)
            pages_data = loader.load_pages()
            total_pages += len(pages_data)

            # Check for scanned pages
            scanned_pages = [p["page"] for p in pages_data if p.get("status") == "text_extraction_failed"]
            if scanned_pages:
                warning_msg = (
                    f"Document '{pdf_path.name}' has {len(scanned_pages)} scanned/image-only page(s) "
                    f"(pages: {scanned_pages}). OCR is required for those pages."
                )
                warnings.append(warning_msg)
                logger.warning(warning_msg)

            chunks = chunker.chunk_pages(pages_data, start_id=current_chunk_id)
            all_chunks.extend(chunks)
            current_chunk_id += len(chunks)

        except Exception as e:
            err_msg = f"Failed to process '{pdf_path.name}': {str(e)}"
            logger.error(err_msg)
            warnings.append(err_msg)

    if not all_chunks:
        get_vector_store().clear_index()
        return {
            "success": False,
            "documents": len(pdf_files),
            "pages": total_pages,
            "chunks": 0,
            "warnings": warnings or ["No extractable text found across documents."]
        }

    # Generate embeddings
    embedding_service = get_embedding_service()
    chunk_texts = [c["text"] for c in all_chunks]
    logger.info(f"Generating embeddings for {len(chunk_texts)} chunks...")
    embeddings = embedding_service.encode_documents(chunk_texts)

    # Build and persist FAISS index
    vector_store = get_vector_store()
    vector_store.build_index(chunks=all_chunks, embeddings=embeddings)

    return {
        "success": True,
        "documents": len(pdf_files),
        "pages": total_pages,
        "chunks": len(all_chunks),
        "warnings": warnings
    }

@router.get("/index/status")
def get_index_status() -> Dict[str, Any]:
    """
    Returns current indexing status and statistics.
    """
    vector_store = get_vector_store()
    stats = vector_store.get_stats()
    
    total_docs_on_disk = len(list(settings.DOCUMENTS_DIR.glob("*.pdf")))
    status_str = "READY" if stats["loaded"] else "NOT INDEXED"

    return {
        "status": status_str,
        "total_documents_on_disk": total_docs_on_disk,
        "indexed_documents_count": stats["unique_documents"],
        "indexed_chunks": stats["total_chunks"],
        "indexed_document_names": stats["document_names"],
        "dimension": stats["dimension"]
    }

@router.post("/load-sample-data")
def load_sample_data() -> Dict[str, Any]:
    """
    Generates realistic sample university regulation PDFs into data/documents/
    and immediately rebuilds the FAISS index.
    """
    try:
        from scripts.generate_sample_regulations import create_sample_pdfs
        create_sample_pdfs(settings.DOCUMENTS_DIR)
        rebuild_result = rebuild_index()
        return {
            "success": True,
            "message": "Sample university regulation documents created and indexed successfully.",
            "index_result": rebuild_result
        }
    except Exception as e:
        logger.error(f"Failed to load sample data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load sample regulations: {str(e)}")
