from sqlalchemy.orm import Session
from backend.models import Conversation,Message
from backend.services.ollama_service import generate_response


def create_conversation(db: Session, title: str, user_id: int):
    try:
        conversation = Conversation(
            title=title,
            user_id=user_id
        )

        db.add(conversation)
        db.commit()
        db.refresh(conversation)

        return conversation

    except Exception:
        db.rollback()
        raise

def get_conversation(db: Session, conversation_id: int, user_id: int):
    return db.query(Conversation).filter(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    ).first()

def get_messages(db: Session, conversation_id: int):
    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).all()

    return messages

async def create_message(db: Session, conversation_id: int, content: str):
    user_message = Message(
        conversation_id=conversation_id,
        role="user",
        content=content
    )

    try:
        db.add(user_message)
        db.commit()
        db.refresh(user_message)

    except Exception:
        db.rollback()
        raise

    messages = db.query(Message).filter(
        Message.conversation_id == conversation_id
    ).order_by(Message.id).all()

    chat_history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages
    ]

    ai_content = await generate_response(chat_history)

    ai_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=ai_content
    )

    db.add(ai_message)
    db.commit()
    db.refresh(ai_message)

    return ai_message
