import os
import requests
import tempfile
from typing import Optional

def fetch_pdf(url: str) -> Optional[str]:
    """
    Downloads a PDF from the given URL to a temporary directory.
    """
    try:
        temp_dir = tempfile.mkdtemp()
        filename = url.split("/")[-1] or "downloaded"
        if not filename.endswith(".pdf"):
            filename += ".pdf"

        local_path = os.path.join(temp_dir, filename)

        response = requests.get(url, timeout=10)
        response.raise_for_status()

        with open(local_path, "wb") as f:
            f.write(response.content)

        return local_path
    except Exception as e:
        print(f"[ERROR] Failed to fetch PDF: {e}")
        return None


def fetch_pdf_from_url(url: str, save_dir: str, filename: str) -> str:
    """
    Downloads a PDF to a specific directory with a specific filename.

    """
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{filename}.pdf")

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    with open(save_path, "wb") as f:
        f.write(response.content)

    return save_path
