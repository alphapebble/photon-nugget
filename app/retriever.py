import chromadb
from chromadb.config import Settings

# Initialize ChromaDB client
chroma_client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="./data/chroma"
))

collection_name = "documents"

# Create or load collection
try:
    collection = chroma_client.get_collection(name=collection_name)
except:
    collection = chroma_client.create_collection(name=collection_name)

# Function to add documents to DB
def add_documents(docs, ids):
    collection.add(documents=docs, ids=ids)

# Function to retrieve relevant chunks
def retrieve_context(query, n_results=3):
    results = collection.query(query_texts=[query], n_results=n_results)
    documents = results["documents"][0] if results["documents"] else []
    return "\n".join(documents)
