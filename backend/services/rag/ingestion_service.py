
from pathlib import Path

from backend.services.rag.document_processor import process_pdf
from backend.services.rag.embedding_service import EmbeddingService
from backend.services.rag.vector_store import VectorStore


class DocumentIngestionService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    def ingest_pdf(
        self,
        file_path: str,
        document_id: str,
        tenant_id: str
    ) -> dict:

        # Step 1: Extract and split the PDF
        chunks = process_pdf(file_path)

        # Step 2: Extract text from each chunk
        texts = [chunk["text"] for chunk in chunks]

        # Step 3: Generate embeddings
        embeddings = self.embedding_service.generate_embeddings(texts)

        # Step 4: Generate unique IDs
        ids = [
            f"{document_id}_page_{chunk['page_number']}_chunk_{chunk['chunk_index']}"
            for chunk in chunks
        ]

        # Step 5: Prepare metadata
        metadatas = [
            {
                "document_id": document_id,
                "tenant_id": tenant_id,
                "page_number": chunk["page_number"],
                "chunk_index": chunk["chunk_index"],
                "file_name": Path(file_path).name
            }
            for chunk in chunks
        ]

        # Step 6: Store everything in ChromaDB
        self.vector_store.add_documents(
            ids=ids,
            texts=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

        return {
            "document_id": document_id,
            "file_name": Path(file_path).name,
            "total_chunks": len(chunks),
            "status": "indexed"
        }
