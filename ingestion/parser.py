from ingestion.cleaner import clean_text

def clean_and_split_text(text, min_words=10):
    """
    Clean extracted text and split into reasonable knowledge chunks.
    """
    chunks = text.split("\n\n")  # Split by double line-breaks = paragraph breaks
    clean_chunks = [chunk.strip().replace('\n', ' ') for chunk in chunks if len(chunk.split()) >= min_words]
    return clean_chunks
