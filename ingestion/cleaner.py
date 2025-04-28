import re

def clean_text(text):
    # Remove extra spaces, newlines, unwanted characters
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s.,]', '', text)  # Keep only words, spaces, commas, dots
    return text.strip()
