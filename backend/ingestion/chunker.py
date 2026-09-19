import re
from typing import List, Dict, Any
from backend.config import settings
from backend.utils.logging_config import logger

class IntelligentChunker:
    """
    Intelligent chunker that splits page text into overlapping windows
    while respecting semantic boundaries (paragraphs, section headers, clauses).
    Preserves exact source document and page number metadata for every chunk.
    """

    def __init__(self, chunk_size: int = settings.CHUNK_SIZE, chunk_overlap: int = settings.CHUNK_OVERLAP):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_pages(self, pages_data: List[Dict[str, Any]], start_id: int = 0) -> List[Dict[str, Any]]:
        """
        Takes a list of page dicts (with 'source', 'page', 'text', 'status')
        and returns chunks with metadata:
        {
            "id": int,
            "source": str,
            "page": int,
            "chunk_id": int,
            "text": str
        }
        """
        chunks: List[Dict[str, Any]] = []
        current_id = start_id

        for page_info in pages_data:
            if page_info.get("status") == "text_extraction_failed":
                continue

            text = page_info.get("text", "").strip()
            if not text:
                continue

            source = page_info["source"]
            page_num = page_info["page"]

            page_chunks = self._split_page_text(text)
            for idx, chunk_text in enumerate(page_chunks):
                chunks.append({
                    "id": current_id,
                    "source": source,
                    "page": page_num,
                    "chunk_id": current_id,
                    "text": chunk_text
                })
                current_id += 1

        logger.info(f"Generated {len(chunks)} chunks from {len(pages_data)} pages")
        return chunks

    def _split_page_text(self, text: str) -> List[str]:
        """
        Splits a single page's text into chunks respecting semantic boundaries.
        If the page is smaller than chunk_size, returns it as a single chunk.
        """
        if len(text) <= self.chunk_size:
            return [text]

        # Break text into structural paragraphs/sections first
        # Split on double newlines or regulation clause patterns (e.g., "\n1.2 ", "\nSection ")
        sections = re.split(r"(\n\n+|\n(?=(?:\d+\.\d+|\b(?:Section|Rule|Article|Clause|Policy)\b)))", text)

        # Merge split delimiters back with sections
        blocks = []
        i = 0
        while i < len(sections):
            curr = sections[i]
            if i + 1 < len(sections) and (sections[i+1].startswith("\n")):
                curr = curr + sections[i+1]
                i += 1
            if curr.strip():
                blocks.append(curr.strip())
            i += 1

        chunks: List[str] = []
        current_chunk = ""

        for block in blocks:
            # If adding this block exceeds chunk_size, save current_chunk and start new
            if len(current_chunk) + len(block) + 1 <= self.chunk_size:
                if current_chunk:
                    current_chunk += "\n\n" + block
                else:
                    current_chunk = block
            else:
                if current_chunk:
                    chunks.append(current_chunk)
                    # Compute overlap from the end of current_chunk
                    overlap_text = self._get_overlap(current_chunk)
                    current_chunk = (overlap_text + "\n\n" + block).strip() if overlap_text else block
                else:
                    # Single block is larger than chunk_size: subdivide by sentence or char
                    sub_chunks = self._subdivide_large_block(block)
                    chunks.extend(sub_chunks[:-1])
                    current_chunk = sub_chunks[-1] if sub_chunks else ""

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks

    def _get_overlap(self, text: str) -> str:
        """Extracts approximately chunk_overlap characters ending at a sentence/word boundary."""
        if len(text) <= self.chunk_overlap:
            return text
        slice_candidate = text[-self.chunk_overlap:]
        # Find first sentence or space break in candidate
        match = re.search(r"[.!?\n]\s+", slice_candidate)
        if match:
            return slice_candidate[match.end():]
        space_idx = slice_candidate.find(" ")
        if space_idx != -1:
            return slice_candidate[space_idx + 1:]
        return slice_candidate

    def _subdivide_large_block(self, block: str) -> List[str]:
        """Subdivides a block that exceeds chunk_size by sentences."""
        sentences = re.split(r"(?<=[.!?])\s+", block)
        sub_chunks = []
        curr = ""

        for s in sentences:
            if len(curr) + len(s) + 1 <= self.chunk_size:
                curr = (curr + " " + s).strip()
            else:
                if curr:
                    sub_chunks.append(curr)
                # If a single sentence exceeds chunk_size, hard slice it
                if len(s) > self.chunk_size:
                    for i in range(0, len(s), self.chunk_size - self.chunk_overlap):
                        sub_chunks.append(s[i:i + self.chunk_size])
                    curr = ""
                else:
                    curr = s
        if curr:
            sub_chunks.append(curr)
        return sub_chunks
