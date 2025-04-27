import lancedb
import pandas as pd
from sentence_transformers import SentenceTransformer

# Initialize LanceDB
db = lancedb.connect("./data/lancedb")  # Local storage

# Load or create the table
try:
    table = db.open_table("documents")
except:
    schema = {
        "vector": lancedb.Vector(384),  # 384 if using all-MiniLM model
        "text": lancedb.Scalar("string")
    }
    table = db.create_table("documents", schema=schema)

# Load embedding model
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')  # Local embeddings

# Function to add documents
def add_documents(docs, ids):
    embeddings = embedding_model.encode(docs).tolist()
    df = pd.DataFrame({
        "vector": embeddings,
        "text": docs
    })
    table.add(df)

# Function to retrieve relevant documents
def retrieve_context(query, n_results=3):
    query_embedding = embedding_model.encode([query])[0].tolist()
    results = table.search(query_embedding).limit(n_results).to_pandas()
    documents = results["text"].tolist()
    return "\n".join(documents)