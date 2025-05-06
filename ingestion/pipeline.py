import os
import requests
import tempfile
import pandas as pd
from sentence_transformers import SentenceTransformer
import lancedb
from typing import Optional

from ingestion.parser import extract_text_from_pdf
from ingestion.cleaner import clean_and_split

import warnings
warnings.filterwarnings("ignore", category=UserWarning)


def fetch_pdf(url: str) -> Optional[str]:
    """
    Downloads a PDF from the given URL to a temporary directory.
    """
    temp_dir = tempfile.mkdtemp()
    filename = url.split("/")[-1] or "temp.pdf"
    if not filename.endswith(".pdf"):
        filename += ".pdf"
    local_path = os.path.join(temp_dir, filename)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        with open(local_path, "wb") as f:
            f.write(response.content)
        print(f"Downloaded PDF from {url}")
        return local_path
    except Exception as e:
        print(f"[ERROR] Failed to fetch PDF from {url}: {e}")
        return None


def is_valid_pdf(file_path: str) -> bool:
    """
    Checks whether a file is a valid PDF by reading its header.
    """
    try:
        with open(file_path, "rb") as f:
            return f.read(4) == b"%PDF"
    except:
        return False


def embed_and_store(chunks: list[str], db_path: str, table_name: str, model_name: str):
    """
    Embeds text chunks and stores them into a LanceDB table.
    """
    embedder = SentenceTransformer(model_name)
    embeddings = embedder.encode(chunks, convert_to_numpy=True).tolist()
    df = pd.DataFrame({"vector": embeddings, "text": chunks})

    db = lancedb.connect(db_path)
    try:
        table = db.open_table(table_name)
        table.add(df)
        print(f"Inserted {len(chunks)} entries into existing table '{table_name}'")
    except:
        db.create_table(table_name, data=df)
        print(f"Created new table '{table_name}' with {len(chunks)} entries")


def run_pipeline(source: str, db_path: str, table_name: str, model_name: str) -> bool:
    """
    Runs the full ingestion pipeline: download (if needed), parse, clean, embed, and store.
    """
    if source.startswith("http://") or source.startswith("https://"):
        source = fetch_pdf(source)
        if not source:
            return False

    if not os.path.exists(source) or not is_valid_pdf(source):
        print(f"[ERROR] File not found or not a valid PDF: {source}")
        return False

    print(f"Extracting text from {source}")
    text = extract_text_from_pdf(source)

    print("Cleaning and splitting text into chunks")
    chunks = clean_and_split(text)

    if not chunks:
        print("[WARNING] No valid text chunks extracted.")
        return False

    embed_and_store(chunks, db_path, table_name, model_name)
    return True
