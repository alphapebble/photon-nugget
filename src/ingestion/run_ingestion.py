import argparse
from ingestion.pipeline import run_pipeline

def main():
    parser = argparse.ArgumentParser(description="Ingest a PDF or batch of URLs into LanceDB.")
    parser.add_argument("pdf_path", nargs="?", help="PDF file path or URL")
    parser.add_argument("--input_file", help="Text file with URLs (one per line)")
    parser.add_argument("--db_path", default="./data/lancedb", help="LanceDB storage path")
    parser.add_argument("--table_name", default="solar_knowledge", help="LanceDB table name")
    parser.add_argument("--model_name", default="all-MiniLM-L6-v2", help="Embedding model")

    args = parser.parse_args()

    if args.input_file:
        with open(args.input_file, "r") as f:
            links = [line.strip() for line in f if line.strip()]
        success = sum(run_pipeline(url, args.db_path, args.table_name, args.model_name) for url in links)
        print(f"{success} succeeded / {len(links)} total")
    elif args.pdf_path:
        success = run_pipeline(args.pdf_path, args.db_path, args.table_name, args.model_name)
        print("Success" if success else "Failed")
    else:
        print("Please provide either a PDF path/URL or an --input_file.")

if __name__ == "__main__":
    main()
