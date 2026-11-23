from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.session import get_db
from backend.models import Conversation,Message,User
from backend.services.ollama_service import generate_response,OllamaTimeoutError,OllamaConnectionError
from backend.schemas import ConversationCreate, ConversationResponse, MessageCreate, MessageResponse
from backend.services.conversation_service import (
    create_conversation as create_conversation_service,
    get_conversation as get_conversation_service,
    get_messages as get_messages_service,
    create_message as create_message_service
)
from backend.dependencies import get_current_user


router = APIRouter(
    prefix="/api/v1/conversations",
    tags = ["Conversations"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=ConversationResponse
)
def create_conversation(
    data: ConversationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return create_conversation_service(
    db, data.title, current_user.id
)
@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = get_conversation_service(
    db, conversation_id, current_user.id
)

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return conversation

@router.post(
    "/{conversation_id}/messages",
    status_code=status.HTTP_201_CREATED,
    response_model=MessageResponse
)
async def create_message(
    conversation_id: int,
    data: MessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = get_conversation_service(db, conversation_id)

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    try:
        return await create_message_service(
            db,
            conversation_id,
            data.content
        )

    except OllamaConnectionError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="AI service is currently unavailable."
        )

    except OllamaTimeoutError:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="AI service request timed out."
        )


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse]
)
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    conversation = get_conversation_service(db, conversation_id)

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    return get_messages_service(db, conversation_id)










