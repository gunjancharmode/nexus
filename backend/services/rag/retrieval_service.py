
from backend.services.rag.embedding_service import EmbeddingService
from backend.services.rag.vector_store import VectorStore


class DocumentRetrievalService:

    def __init__(self):
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore()

    
    def retrieve(
        self,
        question: str,
        tenant_id: str,
        top_k: int = 5,
        distance_threshold: float = 0.7
    ) -> list[dict]:

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        if not tenant_id:
            raise ValueError("Tenant ID is required.")

        if not 0 <= distance_threshold <= 2:
            raise ValueError("Distance threshold must be between 0 and 2.")

        # Step 1: Generate question embedding
        query_embedding = self.embedding_service.generate_embeddings(
            [question]
        )[0]

        # Step 2: Search within this tenant's documents
        results = self.vector_store.search(
            query_embedding=query_embedding,
            n_results=top_k,
            where={"tenant_id": tenant_id}
        )

        # Step 3: Extract search results
        documents = results.get("documents")
        metadatas = results.get("metadatas")
        distances = results.get("distances")

        if not documents or not documents[0]:
            return []

        # Step 4: Filter irrelevant chunks
        retrieved_chunks = []

        for document, metadata, distance in zip(
            documents[0],
            metadatas[0],
            distances[0]
        ):

            print(f"Retrieved chunk distance: {distance:.4f}")

            if distance > distance_threshold:
                continue

            retrieved_chunks.append({
                "text": document,
                "metadata": metadata,
                "distance": distance
            })

        return retrieved_chunks
