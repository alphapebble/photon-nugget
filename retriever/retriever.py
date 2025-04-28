import lancedb
import pandas as pd
from sentence_transformers import SentenceTransformer

# Initialize LanceDB
db = lancedb.connect("./data/lancedb")  # Local storage

# Open the table created during ingestion
table = db.open_table("solar_knowledge")

# Load embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Local embeddings

# Function to retrieve relevant documents
def retrieve_context(query, n_results=3):
    query_embedding = embedding_model.encode([query])[0].tolist()
    results = table.search(query_embedding).limit(n_results).to_pandas()
    documents = results["text"].tolist()
    return "\n".join(documents)

# Optional: quick manual test
if __name__ == "__main__":
    query = "installation procedure of solar modules"
    context = retrieve_context(query)
    print(context)