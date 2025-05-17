import re

def clean_and_split(text: str, chunk_size: int = 300) -> list[str]:
    """
    Clean raw text and split into chunks of ~chunk_size words.
    """
    text = re.sub(r"\s+", " ", text).strip()
    words = text.split()
    return [" ".join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
