from pathlib import Path
from typing import List, Dict, Any
import fitz  # PyMuPDF
from backend.ingestion.cleaner import clean_text
from backend.utils.logging_config import logger

class PDFLoader:
    """
    Extracts text page-by-page from university PDF documents using PyMuPDF.
    Preserves exact page numbers and flags scanned/image-only pages.
    """

    def __init__(self, file_path: str | Path):
        self.file_path = Path(file_path)
        if not self.file_path.exists():
            raise FileNotFoundError(f"PDF file not found: {self.file_path}")

    def load_pages(self) -> List[Dict[str, Any]]:
        """
        Processes the PDF page by page.
        Returns a list of dicts with:
        {
            "source": filename,
            "page": page_number (1-indexed),
            "text": cleaned_text,
            "status": "ok" | "text_extraction_failed"
        }
        """
        pages_data: List[Dict[str, Any]] = []
        filename = self.file_path.name

        try:
            doc = fitz.open(self.file_path)
        except Exception as e:
            logger.error(f"Failed to open PDF {filename}: {str(e)}")
            raise ValueError(f"Corrupted or invalid PDF file: {filename}") from e

        try:
            total_pages = len(doc)
            logger.info(f"Loading '{filename}' ({total_pages} pages)")

            scanned_pages_count = 0

            for page_index in range(total_pages):
                page_number = page_index + 1
                try:
                    page = doc.load_page(page_index)
                    raw_text = page.get_text("text")
                    cleaned = clean_text(raw_text)

                    if not cleaned or len(cleaned.strip()) < 10:
                        # Page contains no extractable text -> scanned or image-only
                        scanned_pages_count += 1
                        logger.warning(
                            f"Page {page_number} in '{filename}' has no extractable text. "
                            f"Marking as 'text_extraction_failed' (scanned/image-only page)."
                        )
                        pages_data.append({
                            "source": filename,
                            "page": page_number,
                            "text": "",
                            "status": "text_extraction_failed",
                            "warning": "This page appears to contain scanned/image-only content. OCR is required."
                        })
                    else:
                        pages_data.append({
                            "source": filename,
                            "page": page_number,
                            "text": cleaned,
                            "status": "ok"
                        })
                except Exception as page_err:
                    logger.warning(f"Error reading page {page_number} of '{filename}': {str(page_err)}")
                    pages_data.append({
                        "source": filename,
                        "page": page_number,
                        "text": "",
                        "status": "text_extraction_failed",
                        "warning": f"Page read error: {str(page_err)}"
                    })

            if scanned_pages_count == total_pages and total_pages > 0:
                logger.warning(
                    f"Document '{filename}' appears to be entirely scanned or image-only. "
                    "OCR is required for text extraction."
                )

            return pages_data
        finally:
            doc.close()
