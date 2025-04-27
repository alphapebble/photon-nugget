import os
import argparse
import pandas as pd
from sentence_transformers import SentenceTransformer
import lancedb

from ingestion.fetcher import extract_text_from_pdf
from ingestion.parser import clean_and_split_text

def embed_and_store(chunks, db_path="./data/lancedb", table_name="solar_knowledge"):
    """
    Embed chunks using SentenceTransformer and store into LanceDB.
    """
    db = lancedb.connect(db_path)

    try:
        table = db.open_table(table_name)
    except:
        schema = {
            "vector": lancedb.Vector(384),
            "text": lancedb.Scalar("string")
        }
        table = db.create_table(table_name, schema=schema)

    embedder = SentenceTransformer('all-MiniLM-L6-v2')
    embeddings = embedder.encode(chunks, convert_to_numpy=True).tolist()
    df = pd.DataFrame({"vector": embeddings, "text": chunks})

    table.add(df)
    print(f"✅ Successfully embedded and stored {len(chunks)} chunks.")

def ingest_pdf_to_lancedb(pdf_path, db_path="./data/lancedb", table_name="solar_knowledge"):
    """
    Full ingestion pipeline for a PDF file.
    """
    print(f"🚀 Processing {pdf_path}...")
    text = extract_text_from_pdf(pdf_path)
    chunks = clean_and_split_text(text)
    embed_and_store(chunks, db_path=db_path, table_name=table_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest solar PDF into LanceDB.")
    parser.add_argument("pdf_path", type=str, help="Path to the PDF file.")
    parser.add_argument("--db_path", type=str, default="./data/lancedb", help="Path to LanceDB directory.")
    parser.add_argument("--table_name", type=str, default="solar_knowledge", help="LanceDB table name.")
    args = parser.parse_args()

    if os.path.exists(args.pdf_path):
        ingest_pdf_to_lancedb(args.pdf_path, db_path=args.db_path, table_name=args.table_name)
    else:
        print(f"File not found: {args.pdf_path}")