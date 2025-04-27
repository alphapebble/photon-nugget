import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path):
    """
    Extract full text from a PDF using PyMuPDF (fitz).
    """
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    return full_text
