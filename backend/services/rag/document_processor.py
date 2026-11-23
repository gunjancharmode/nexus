from backend.services.rag.document_loader import load_pdf
from backend.services.rag.text_splitter import split_text

def process_pdf(file_path:str) -> list[dict]:
    """
    Extract PDF text and divide it into chunks.
    Preserve page numbers and chunk information.
    """

    pages = load_pdf(file_path)

    processed_chunks = []

    for page in pages:
        chunks = split_text(page["text"])

        for chunk_index,chunk in enumerate(chunks):
            processed_chunks.append({
                "text":chunk,
                "page_number":page["page_number"],
                "chunk_index":chunk_index
            })

    return processed_chunks
