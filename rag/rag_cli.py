import argparse
from .rag_engine import rag_answer

def main():
    parser = argparse.ArgumentParser(description="Ask a solar question via RAG")
    parser.add_argument("query", type=str, help="Your question")
    args = parser.parse_args()

    response = rag_answer(args.query)
    print("\n=== Response ===")
    print(response)

if __name__ == "__main__":
    main()
