import os
import argparse
import pandas as pd
import requests
import tempfile
from sentence_transformers import SentenceTransformer
import lancedb

from ingestion.fetcher import extract_text_from_pdf
from ingestion.parser import clean_and_split_text


def download_pdf_to_temp(url):
    temp_dir = tempfile.mkdtemp()
    filename = url.split("/")[-1]
    local_path = os.path.join(temp_dir, filename)

    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(response.content)
        print(f"Successfully downloaded {filename}")
        return local_path
    except Exception as e:
        print(f"Failed to download {url}: {str(e)}")
        return None

def is_valid_pdf(file_path):
    try:
        with open(file_path, "rb") as f:
            header = f.read(4)
            return header == b"%PDF"
    except Exception as e:
        print(f"Error checking file {file_path}: {str(e)}")
        return False

def embed_and_store(chunks, db_path="./data/lancedb", table_name="solar_knowledge", model_name="all-MiniLM-L6-v2"):
    db = lancedb.connect(db_path)

    try:
        table = db.open_table(table_name)
    except Exception:
        embedder = SentenceTransformer(model_name)
        embeddings = embedder.encode(chunks, convert_to_numpy=True).tolist()

        df = pd.DataFrame({"vector": embeddings, "text": chunks})

        table = db.create_table(table_name, data=df)
        print(f"Created new table and inserted {len(chunks)} chunks.")
        return

    # If table already exists, then insert more rows
    embedder = SentenceTransformer(model_name)
    embeddings = embedder.encode(chunks, convert_to_numpy=True).tolist()

    df = pd.DataFrame({"vector": embeddings, "text": chunks})

    table.add(df)
    print(f"Inserted {len(chunks)} chunks into existing table.")


def ingest_pdf_to_lancedb(source_path, db_path="./data/lancedb", table_name="solar_knowledge", model_name="all-MiniLM-L6-v2"):
    if source_path.startswith("http://") or source_path.startswith("https://"):
        pdf_path = download_pdf_to_temp(source_path)
        if not pdf_path:
            print(f"Failed to process URL: {source_path}")
            return False
    else:
        pdf_path = source_path

    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return False

    if not is_valid_pdf(pdf_path):
        print(f"Invalid or corrupted PDF file: {pdf_path}. Skipping.")
        return False

    print(f"Processing {pdf_path}...")
    text = extract_text_from_pdf(pdf_path)
    chunks = clean_and_split_text(text)
    embed_and_store(chunks, db_path=db_path, table_name=table_name, model_name=model_name)
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest PDF(s) into LanceDB.")
    parser.add_argument("pdf_path", nargs="?", type=str, help="Path to the PDF file or a URL.")
    parser.add_argument("--input_file", type=str, help="Path to a text file containing list of URLs.")
    parser.add_argument("--db_path", type=str, default="./data/lancedb", help="Path to LanceDB directory.")
    parser.add_argument("--table_name", type=str, default="solar_knowledge", help="LanceDB table name.")
    parser.add_argument("--model_name", type=str, default="all-MiniLM-L6-v2", help="SentenceTransformer model name to use.")

    args = parser.parse_args()

    if args.input_file:
        success_count = 0
        fail_count = 0
        with open(args.input_file, 'r') as f:
            links = [line.strip() for line in f if line.strip()]
        for link in links:
            if ingest_pdf_to_lancedb(link, db_path=args.db_path, table_name=args.table_name, model_name=args.model_name):
                success_count += 1
            else:
                fail_count += 1
        print(f"Summary: {success_count} successful, {fail_count} failed.")
    elif args.pdf_path:
        if ingest_pdf_to_lancedb(args.pdf_path, db_path=args.db_path, table_name=args.table_name, model_name=args.model_name):
            print("Ingestion completed successfully.")
        else:
            print("Ingestion failed.")
    else:
        print("Provide either a PDF path/URL or an --input_file.")
