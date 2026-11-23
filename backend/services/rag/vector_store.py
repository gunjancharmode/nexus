
import chromadb


class VectorStore:

    def __init__(self, collection_name: str = "nexus_documents"):

        self.client = chromadb.PersistentClient(
            path="./chroma_data"
        )

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

    def add_documents(
        self,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict]
    ) -> None:

        if not texts:
            return

        if not (
            len(ids) == len(texts) ==
            len(embeddings) == len(metadatas)
        ):
            raise ValueError("All input lists must have equal lengths.")

        self.collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )

    def search(
        self,
        query_embedding: list[float],
        n_results: int = 5,
        where: dict | None = None
    ) -> dict:

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where
        )

        return results

    def get_documents(self, tenant_id: str) -> dict:

        results = self.collection.get(
            where={"tenant_id": tenant_id},
            include=["metadatas"]
        )

        return results

    def delete_document(self,
        document_id: str,
        tenant_id: str
    ) -> int:

        results = self.collection.get(
            where={
                "$and": [
                    {"document_id": document_id},
                    {"tenant_id": tenant_id}
                ]
            },
            include=[]
        )

        ids = results.get("ids", [])

        if not ids:
            return 0

        self.collection.delete(ids=ids)

        return len(ids)
