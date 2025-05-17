import lancedb
import pandas as pd
from sentence_transformers import SentenceTransformer
from typing import List

# Global setup
DB_PATH = "./data/lancedb"
TABLE_NAME = "solar_knowledge"
EMBED_MODEL = "all-MiniLM-L6-v2"

# Load LanceDB and embedding model
db = lancedb.connect(DB_PATH)

# Check if the table exists, if not create a sample table
try:
    table = db.open_table(TABLE_NAME)
except ValueError as e:
    if "Table 'solar_knowledge' was not found" in str(e):
        import numpy as np
        from datetime import datetime
        import os

        print(f"Table {TABLE_NAME} not found. Creating a sample table...")

        # Create sample data
        data = [
            {
                "text": "Solar panels convert sunlight into electricity through the photovoltaic effect.",
                "vector": np.random.rand(384).astype(np.float32),  # Random embedding vector
                "metadata": {
                    "source_type": "text",
                    "created_at": datetime.now().isoformat()
                }
            },
            {
                "text": "Regular maintenance of solar panels includes cleaning and inspection for optimal performance.",
                "vector": np.random.rand(384).astype(np.float32),  # Random embedding vector
                "metadata": {
                    "source_type": "text",
                    "created_at": datetime.now().isoformat()
                }
            }
        ]

        # Create the table
        table = db.create_table(TABLE_NAME, data)
        print(f"Sample table {TABLE_NAME} created successfully")
    else:
        raise

# Load embedding model
embedding_model = SentenceTransformer(EMBED_MODEL)


def get_context_documents(query: str, n_results: int = 3) -> List[str]:
    """
    Retrieve top-n relevant document chunks for a query from LanceDB.
    """
    # Disable progress bar to avoid I/O error
    query_embedding = embedding_model.encode([query], show_progress_bar=False)[0].tolist()
    results_df = table.search(query_embedding).limit(n_results).to_pandas()
    return results_df["text"].tolist()


# Optional test
if __name__ == "__main__":
    sample_query = "installation procedure of solar modules"
    docs = get_context_documents(sample_query)
    print("\n".join(docs))
