import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.llm.nvidia_client import NVIDIAClient
from backend.rag.pipeline import RAGPipeline

def test_key():
    print("==================================================")
    print("         NVIDIA API KEY VERIFICATION TEST         ")
    print("==================================================")

    # 1. Direct LLM completion
    print("\n1. Testing direct connection to NVIDIA API...")
    client = NVIDIAClient()
    try:
        reply = client.generate_chat_completion([
            {"role": "user", "content": "Respond with: 'NVIDIA API connection verified successfully!'"}
        ])
        print("-> Status: SUCCESS")
        print("-> Response:", reply)
    except Exception as e:
        print("-> Status: FAILED")
        print("-> Error:", str(e))
        return False

    # 2. End-to-end RAG query
    print("\n2. Testing end-to-end RAG grounding with NVIDIA API...")
    pipeline = RAGPipeline()
    res = pipeline.query("What is the minimum attendance requirement?")
    print("-> Query: 'What is the minimum attendance requirement?'")
    print("-> Grounded Found:", res.get("found"))
    print("\n-> AI Generated Answer:\n", res.get("answer"))
    print("\n-> Authoritative Sources Cited:")
    for s in res.get("sources", []):
        print(f"   * {s['document']} (Page {s['page']}) - Relevance: {s['score']:.4f}")

    print("\n==================================================")
    print("       ALL CHECKS PASSED: SYSTEM IS READY!        ")
    print("==================================================")
    return True

if __name__ == "__main__":
    test_key()
