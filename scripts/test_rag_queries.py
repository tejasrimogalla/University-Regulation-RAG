import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from backend.rag.pipeline import RAGPipeline

def run_evaluation():
    pipeline = RAGPipeline()

    test_cases = [
        "What is the minimum attendance requirement?",
        "What are the eligibility requirements for semester examinations?",
        "Can attendance shortage be condoned?",
        "What is the supplementary examination rule?",
        "What is the university's policy on Mars colonization?"
    ]

    print("\n=======================================================")
    print("      UNIVERSITY REGULATION RAG EVALUATION SUITE       ")
    print("=======================================================\n")

    for idx, query in enumerate(test_cases, start=1):
        print(f"\n--- TEST CASE {idx} ---")
        print(f"QUERY: {query}")
        result = pipeline.query(query)

        print(f"FOUND: {result.get('found')}")
        print(f"SOURCES RETRIEVED: {len(result.get('sources', []))}")
        
        for s in result.get("sources", []):
            print(f"  * Document: {s['document']} | Page: {s['page']} | Relevance: {s['score']:.4f}")

        answer = result.get('answer', '')
        print("\nANSWER:")
        print(answer)
        print("-" * 55)

if __name__ == "__main__":
    run_evaluation()
