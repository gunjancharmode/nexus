
from pathlib import Path
from functools import lru_cache
from uuid import uuid4,UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)
from pydantic import BaseModel, Field

from backend.dependencies import get_current_user
from backend.models import User
from backend.services.rag.ingestion_service import DocumentIngestionService
from backend.services.rag.rag_service import RAGService
from backend.services.rag.vector_store import VectorStore


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"],
)

UPLOAD_DIR = Path("storage/uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024


class AskDocumentRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


@lru_cache
def get_ingestion_service():
    return DocumentIngestionService()


@lru_cache
def get_rag_service():
    return RAGService()

@lru_cache
def get_vector_store():
    return VectorStore()

@router.get("/")
def list_documents(
    current_user: User = Depends(get_current_user),
    vector_store: VectorStore = Depends(get_vector_store),
):
    try:
        results = vector_store.get_documents(
            tenant_id=str(current_user.id)
        )

        documents = {}

        metadatas = results.get("metadatas") or []

        for metadata in metadatas:

            document_id = metadata.get("document_id")

            if not document_id:
                continue

            if document_id not in documents:
                documents[document_id] = {
                    "document_id": document_id,
                    "file_name": metadata.get("file_name"),
                    "total_chunks": 0,
                    "pages": set(),
                }

            documents[document_id]["total_chunks"] += 1

            page_number = metadata.get("page_number")

            if page_number is not None:
                documents[document_id]["pages"].add(page_number)

        document_list = []

        for document in documents.values():
            document["pages"] = sorted(document["pages"])
            document_list.append(document)

        return {
            "total": len(document_list),
            "documents": document_list,
        }

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve documents: {str(error)}",
        ) from error


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    ingestion_service: DocumentIngestionService = Depends(
        get_ingestion_service
    ),
):
    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed.",
        )

    document_id = str(uuid4())

    user_upload_dir = UPLOAD_DIR / str(current_user.id)
    user_upload_dir.mkdir(parents=True, exist_ok=True)

    file_path = user_upload_dir / f"{document_id}.pdf"

    total_size = 0
    first_chunk = True

    try:
        with file_path.open("wb") as destination:

            while True:
                chunk = file.file.read(1024 * 1024)

                if not chunk:
                    break

                if first_chunk:
                    if not chunk.startswith(b"%PDF-"):
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Invalid PDF file.",
                        )
                    first_chunk = False

                total_size += len(chunk)

                if total_size > MAX_FILE_SIZE:
                    raise HTTPException(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        detail="File size cannot exceed 10 MB.",
                    )

                destination.write(chunk)

        if total_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty.",
            )

        result = ingestion_service.ingest_pdf(
            file_path=str(file_path),
            document_id=document_id,
            tenant_id=str(current_user.id),
        )

        return {
            "message": "Document uploaded and indexed successfully.",
            **result,
        }

    except HTTPException:
        file_path.unlink(missing_ok=True)
        raise

    except Exception as error:
        file_path.unlink(missing_ok=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document processing failed: {str(error)}",
        ) from error

    finally:
        file.file.close()


@router.post("/ask")
async def ask_document_question(
    request: AskDocumentRequest,
    current_user: User = Depends(get_current_user),
    rag_service: RAGService = Depends(get_rag_service),
):
    try:
        result = await rag_service.ask(
            question=request.question,
            tenant_id=str(current_user.id),
        )

        return result

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Question answering failed: {str(error)}",
        ) from error


@router.delete("/{document_id}")
def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    vector_store: VectorStore = Depends(get_vector_store),
):
    # Step 1: Validate document ID
    try:
        UUID(document_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid document ID.",
        )

    tenant_id = str(current_user.id)

    try:
        # Step 2: Check document ownership
        results = vector_store.get_documents(
            tenant_id=tenant_id
        )

        metadatas = results.get("metadatas") or []

        document_exists = any(
            metadata.get("document_id") == document_id
            for metadata in metadatas
        )

        if not document_exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        # Step 3: Delete vectors from ChromaDB
        deleted_chunks = vector_store.delete_document(
            document_id=document_id,
            tenant_id=tenant_id,
        )

        if deleted_chunks == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found.",
            )

        # Step 4: Delete PDF from user's upload directory
        file_path = (
            UPLOAD_DIR
            / tenant_id
            / f"{document_id}.pdf"
        )

        file_path.unlink(missing_ok=True)

        # Step 5: Return response
        return {
            "message": "Document deleted successfully.",
            "document_id": document_id,
            "deleted_chunks": deleted_chunks,
        }

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document deletion failed: {str(error)}",
        ) from error
