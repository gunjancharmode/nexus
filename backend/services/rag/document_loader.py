from pathlib import Path
from pypdf import PdfReader

def load_pdf(file_path: str) -> list[dict]:
    """
    Extract text from a PDF file page by page
    """

    pdf_path = Path(file_path)

    if not pdf_path.exists():
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    if not pdf_path.is_file():
        raise ValueError(f"Path is not a file: {file_path}")

    try:
        reader = PdfReader(pdf_path)

        if reader.is_encrypted:
            raise ValueError("Encrypted PDFs are not supported yet.")

        documents = []

        for page_number, page in enumerate(reader.pages, start=1):
            text = page.extract_text()

            if text and text.strip():
                documents.append({
                    "page_number": page_number,
                    "text": text.strip()
                })

        if not documents:
            raise ValueError("PDF contains no extractable text.")

        return documents
    except ValueError:
        raise

    except Exception as error:
        raise ValueError(f"Failed to read pdf: {error}") from error
    