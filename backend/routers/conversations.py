from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.session import get_db
from backend.models import Conversation,Message
from backend.schemas import ConversationCreate, ConversationResponse, MessageCreate, MessageResponse

router = APIRouter(
    prefix="/api/v1/conversations",
    tags = ["Conversations"])


@router.post("/", status_code= status.HTTP_201_CREATED,response_model=ConversationResponse)
def create_conversation(data: ConversationCreate,db: Session = Depends(get_db)):
    conversation = Conversation(title = data.title)

    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    return conversation

@router.get("/{conversation_id}",response_model=ConversationResponse)
def get_conversation(conversation_id: int,db: Session = Depends(get_db)):
    conversations = db.query(Conversation).filter(Conversation.id == conversation_id).first()

    if conversations is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,detail="Conversation not found"
        )
    return conversations

@router.post("/{conversation_id}/messages",status_code=status.HTTP_201_CREATED,response_model=MessageResponse)
def create_message(conversation_id: int,data:MessageCreate,db:Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()

    if conversation is None:
        raise HTTPException(
            status_code= status.HTTP_408_REQUEST_TIMEOUT,
            detail= "Conversation not found"
        )
    message = Message(
        conversation_id = conversation_id,
        role = "user",
        content = data.content
    )
    db.add(message)
    db.commit()
    db.refresh(message)

    return message


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse]
)
def get_messages(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    conversation = db.query(Conversation).filter(
        Conversation.id == conversation_id
    ).first()

    if conversation is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found"
        )

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).all()

    return messages










