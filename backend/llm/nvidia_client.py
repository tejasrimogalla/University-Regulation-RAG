from typing import List, Dict, Any, Optional
import httpx
from backend.config import settings
from backend.utils.logging_config import logger

class NVIDIAClientError(Exception):
    """Base exception for NVIDIA API client errors."""
    pass

class NVIDIAAuthError(NVIDIAClientError):
    """Raised when NVIDIA API authentication fails."""
    pass

class NVIDIARateLimitError(NVIDIAClientError):
    """Raised when NVIDIA API rate limit is reached."""
    pass

class NVIDIATimeoutError(NVIDIAClientError):
    """Raised when NVIDIA API request times out."""
    pass

class NVIDIAClient:
    """
    Dedicated client for calling the NVIDIA OpenAI-compatible Chat Completions API.
    All requests originate from the backend. The API key is NEVER sent to the frontend.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 45.0
    ):
        self.api_key = api_key if api_key is not None else settings.NVIDIA_API_KEY
        self.base_url = base_url if base_url is not None else settings.NVIDIA_BASE_URL
        self.model = model if model is not None else settings.NVIDIA_MODEL
        self.timeout = timeout

    def is_configured(self) -> bool:
        """Checks if the NVIDIA API key is set and not a placeholder."""
        return bool(self.api_key and self.api_key.strip() != "YOUR_NVIDIA_API_KEY")

    def generate_chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.0,
        max_tokens: int = 1024
    ) -> str:
        """
        Sends a synchronous chat completion request to the NVIDIA API.
        Returns the generated text response.
        """
        if not self.is_configured():
            logger.error("NVIDIA_API_KEY is not configured or still set to placeholder.")
            raise NVIDIAAuthError(
                "NVIDIA API Key is missing or unconfigured. "
                "Please set your NVIDIA_API_KEY in backend/.env"
            )

        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": 1.0,
            "stream": False
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(endpoint, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                choices = data.get("choices", [])
                if not choices:
                    logger.warning("NVIDIA API returned empty choices list.")
                    return "No response generated from the model."
                
                content = choices[0].get("message", {}).get("content", "").strip()
                return content

            elif response.status_code in (401, 403):
                logger.error(f"NVIDIA API authentication failed ({response.status_code}): {response.text}")
                raise NVIDIAAuthError("Invalid or unauthorized NVIDIA API key. Please check your credentials.")

            elif response.status_code == 429:
                logger.error(f"NVIDIA API rate limit exceeded: {response.text}")
                raise NVIDIARateLimitError("NVIDIA API rate limit exceeded. Please wait a moment and try again.")

            elif response.status_code in (400, 404):
                logger.error(f"NVIDIA API request error ({response.status_code}): {response.text}")
                raise NVIDIAClientError(
                    f"NVIDIA API model error ({self.model}): {response.text}. "
                    "Ensure the model is valid and accessible on your NVIDIA API account."
                )

            else:
                logger.error(f"NVIDIA API returned unexpected status {response.status_code}: {response.text}")
                raise NVIDIAClientError(f"NVIDIA API error ({response.status_code}): {response.text}")

        except httpx.TimeoutException as e:
            logger.error(f"NVIDIA API request timed out after {self.timeout}s: {str(e)}")
            raise NVIDIATimeoutError(f"NVIDIA API request timed out after {self.timeout} seconds.") from e
        except httpx.RequestError as e:
            logger.error(f"Network error connecting to NVIDIA API: {str(e)}")
            raise NVIDIAClientError(f"Network error communicating with NVIDIA API: {str(e)}") from e

_nvidia_client: Optional[NVIDIAClient] = None

def get_nvidia_client() -> NVIDIAClient:
    global _nvidia_client
    if _nvidia_client is None:
        _nvidia_client = NVIDIAClient()
    return _nvidia_client
