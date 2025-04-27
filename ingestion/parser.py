def clean_and_split_text(text, min_words=10):
    """
    Clean extracted text and split into reasonable knowledge chunks.
    """
    chunks = text.split("\n\n")  # Split on paragraph breaks
    clean_chunks = [chunk.strip().replace('\n', ' ') for chunk in chunks if len(chunk.split()) >= min_words]
    return clean_chunks
