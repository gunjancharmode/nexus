
from sqlalchemy import String, Text, ForeignKey,Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime, timezone

class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)

class Conversation(Base):
    __tablename__ = "conversations"

    id: Mapped[int] = mapped_column(primary_key=True)
    user: Mapped["User"] = relationship()
    title : Mapped[str] = mapped_column(String(200),nullable=False, default="new conversation")
    created_at: Mapped[datetime] = mapped_column(default=lambda: datetime.now(timezone.utc))
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation",cascade="all, delete-orphan")
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"),nullable=False)

class Message(Base):
    __tablename__ = 'messages'

    id: Mapped[int] = mapped_column(primary_key=True)
    conversation_id: Mapped[int] = mapped_column(ForeignKey("conversations.id"),nullable=False)
    role: Mapped[str] = mapped_column(String(20),nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    conversation: Mapped['Conversation'] = relationship(back_populates='messages')

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100),nullable=False)
    email: Mapped[str] = mapped_column(String(255),unique=True,nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255),nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean,default=True,nullable=False)
