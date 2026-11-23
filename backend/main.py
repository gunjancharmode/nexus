
from fastapi import Depends, FastAPI, HTTPException, Query ,status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.routers.conversations import router as conversations_router
from backend.services.ollama_service import generate_response
from backend.database import engine
from backend.models import Base, Customer
from backend.schemas import CustomerCreate, CustomerResponse
from backend.session import SessionLocal
from backend.routers.auth import router as auth_router
from backend.routers.documents import router as documents_router

app = FastAPI(
    title="NEXUS API",
    description="Enterprise AI platform API",
    version="0.1.0",    
)

app.include_router(conversations_router)
app.include_router(auth_router)
app.include_router(conversations_router)
app.include_router(auth_router)
app.include_router(documents_router)

class ChatRequest(BaseModel):
    messages: list[dict[str, str]]


@app.post("/api/v1/llm")
async def ask_llm(request: ChatRequest):
    ai_response = await generate_response(request.messages)
    return {"response": ai_response}


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/api/v1/health")
def health_check():
    return {
        "status": "ok",
        "service": "nexus-api",
        "version": "0.1.0",
    }


@app.post(
    "/api/v1/customers",
    response_model=CustomerResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_customer(
    customer_data: CustomerCreate,
    db: Session = Depends(get_db),
):
    existing_customer = (
        db.query(Customer)
        .filter(Customer.email == customer_data.email)
        .first()
    )

    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A customer with this email already exists.",
        )

    customer = Customer(
        name=customer_data.name,
        email=str(customer_data.email),
    )

    try:
        db.add(customer)
        db.commit()
        db.refresh(customer)
        return customer
    except Exception:
        db.rollback()
        raise





@app.get(
    "/api/v1/customers",
    response_model=list[CustomerResponse],
)
def list_customers(
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
):
    customers = (
        db.query(Customer)
        .order_by(Customer.id)
        .offset(offset)
        .limit(limit)
        .all()
    )

    return customers
