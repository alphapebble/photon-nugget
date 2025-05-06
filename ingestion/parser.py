import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract full text from a PDF using PyMuPDF.
    """
    with fitz.open(pdf_path) as doc:
        return "\n".join(page.get_text() for page in doc)
