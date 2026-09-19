from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, status
from backend.rag.pipeline import RAGPipeline
from backend.utils.logging_config import logger

router = APIRouter(prefix="", tags=["chat"])

class ChatHistoryTurn(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text")

class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=2000, description="User question about university regulations")
    conversation_history: Optional[List[ChatHistoryTurn]] = Field(default=None, description="Previous conversation turns")

class SourceCitation(BaseModel):
    document: str
    page: int
    score: float
    text: str
    chunk_id: Optional[int] = None

class ChatResponse(BaseModel):
    answer: str
    found: bool
    sources: List[SourceCitation]
    error: Optional[str] = None

_pipeline: Optional[RAGPipeline] = None

def get_pipeline() -> RAGPipeline:
    global _pipeline
    if _pipeline is None:
        _pipeline = RAGPipeline()
    return _pipeline

@router.post("/chat", response_model=ChatResponse)
def ask_question(request: ChatRequest) -> ChatResponse:
    """
    Submits a student question to the RAG pipeline.
    Retrieves grounded evidence from indexed regulations, queries NVIDIA API,
    and returns authoritative answer and source document/page citations.
    """
    question = request.question.strip()
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The question cannot be empty."
        )

    pipeline = get_pipeline()
    history_dicts = (
        [{"role": turn.role, "content": turn.content} for turn in request.conversation_history]
        if request.conversation_history else None
    )

    try:
        result = pipeline.query(
            question=question,
            conversation_history=history_dicts
        )
        return ChatResponse(
            answer=result.get("answer", ""),
            found=result.get("found", False),
            sources=[
                SourceCitation(
                    document=s.get("document", ""),
                    page=s.get("page", 1),
                    score=s.get("score", 0.0),
                    text=s.get("text", ""),
                    chunk_id=s.get("chunk_id")
                )
                for s in result.get("sources", [])
            ],
            error=result.get("error")
        )
    except Exception as e:
        logger.error(f"Error in /chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate an answer. Please check backend logs."
        )
