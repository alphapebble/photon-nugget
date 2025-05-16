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
table = db.open_table(TABLE_NAME)
embedding_model = SentenceTransformer(EMBED_MODEL)


def get_context_documents(query: str, n_results: int = 3) -> List[str]:
    """
    Retrieve top-n relevant document chunks for a query from LanceDB.
    """
    query_embedding = embedding_model.encode([query])[0].tolist()
    results_df = table.search(query_embedding).limit(n_results).to_pandas()
    return results_df["text"].tolist()


# Optional test
if __name__ == "__main__":
    sample_query = "installation procedure of solar modules"
    docs = get_context_documents(sample_query)
    print("\n".join(docs))
