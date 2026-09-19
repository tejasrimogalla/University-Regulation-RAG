from typing import List, Dict, Any, Optional
from backend.rag.retriever import RegulationRetriever
from backend.rag.prompt import (
    build_context_block,
    build_messages,
    NOT_FOUND_MESSAGE
)
from backend.llm.nvidia_client import (
    get_nvidia_client,
    NVIDIAClientError,
    NVIDIAAuthError,
    NVIDIARateLimitError,
    NVIDIATimeoutError
)
from backend.utils.logging_config import logger

class RAGPipeline:
    """
    End-to-end RAG pipeline for University Regulations.
    Coordinates retrieval, grounding verification, NVIDIA LLM generation,
    and authoritative source attribution.
    """

    def __init__(self, retriever: Optional[RegulationRetriever] = None):
        self.retriever = retriever or RegulationRetriever()
        self.nvidia_client = get_nvidia_client()

    def query(
        self,
        question: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        top_k: Optional[int] = None,
        min_similarity: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Processes a user question and returns a grounded response with source citations.
        Enforces dual-layer 'Not Found' defense.
        """
        cleaned_question = question.strip() if question else ""
        if not cleaned_question:
            return {
                "answer": "Please provide a valid question about university regulations.",
                "found": False,
                "sources": []
            }

        # Step 1: Retrieve relevant regulation chunks
        retrieved_chunks = self.retriever.retrieve(
            query=cleaned_question,
            top_k=top_k,
            min_similarity=min_similarity
        )

        # LAYER 1 DEFENSE: If no chunks pass the similarity threshold,
        # IMMEDIATELY return not-found without invoking NVIDIA API.
        if not retrieved_chunks:
            logger.info(f"Layer 1 Defense Triggered: No chunks above threshold for '{cleaned_question}'.")
            return {
                "answer": NOT_FOUND_MESSAGE,
                "found": False,
                "sources": []
            }

        # Step 2: Build context block and chat messages
        context_str = build_context_block(retrieved_chunks)
        messages = build_messages(
            query=cleaned_question,
            context=context_str,
            conversation_history=conversation_history
        )

        # Step 3: Invoke NVIDIA API
        try:
            logger.info(f"Invoking NVIDIA API ({self.nvidia_client.model}) for grounded generation...")
            raw_answer = self.nvidia_client.generate_chat_completion(
                messages=messages,
                temperature=0.0
            )
        except NVIDIAAuthError as e:
            logger.warning(f"NVIDIA API authentication unconfigured: {str(e)}. Providing direct grounded excerpt.")
            top_source = retrieved_chunks[0]
            excerpt_answer = (
                f"**Direct University Regulation Excerpt:**\n\n"
                f"{top_source['text']}\n\n"
                f"---\n"
                f"*Note: Configure `NVIDIA_API_KEY` in `backend/.env` for AI-synthesized summaries. "
                f"The authoritative source document and page number are cited below.*"
            )
            return {
                "answer": excerpt_answer,
                "found": True,
                "sources": retrieved_chunks,
                "error": "NVIDIA API Key not configured in backend/.env (Showing verified document excerpt)"
            }
        except NVIDIARateLimitError as e:
            logger.error(f"Rate limit calling NVIDIA API: {str(e)}")
            return {
                "answer": "Error: NVIDIA API rate limit reached. Please wait a moment before trying again.",
                "found": False,
                "sources": retrieved_chunks,
                "error": "rate_limit"
            }
        except NVIDIATimeoutError as e:
            logger.error(f"Timeout calling NVIDIA API: {str(e)}")
            return {
                "answer": "Error: NVIDIA API request timed out. Please try your request again.",
                "found": False,
                "sources": retrieved_chunks,
                "error": "timeout"
            }
        except NVIDIAClientError as e:
            logger.error(f"NVIDIA API client error: {str(e)}")
            return {
                "answer": f"Error communicating with NVIDIA API: {str(e)}",
                "found": False,
                "sources": retrieved_chunks,
                "error": "client_error"
            }
        except Exception as e:
            logger.error(f"Unexpected error during RAG generation: {str(e)}", exc_info=True)
            return {
                "answer": "An unexpected error occurred while generating the answer. Please check backend logs.",
                "found": False,
                "sources": retrieved_chunks,
                "error": "unexpected_error"
            }

        # LAYER 2 DEFENSE: Check if the model explicitly indicated not-found
        answer_lower = raw_answer.lower().strip()
        is_not_found = (
            "couldn't find this information" in answer_lower or
            "could not find this information" in answer_lower or
            "cannot find this information" in answer_lower or
            "not found in the available" in answer_lower
        )

        if is_not_found:
            logger.info(f"Layer 2 Defense Triggered: Model reported information not in context.")
            return {
                "answer": NOT_FOUND_MESSAGE,
                "found": False,
                "sources": []
            }

        return {
            "answer": raw_answer,
            "found": True,
            "sources": retrieved_chunks
        }
