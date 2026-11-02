import httpx
from fastapi import Depends, FastAPI, HTTPException, Query ,status
from sqlalchemy.orm import Session

from backend.database import engine
from backend.models import Base, Customer
from backend.schemas import CustomerCreate, CustomerResponse
from backend.session import SessionLocal

app = FastAPI(
    title="NEXUS API",
    description="Enterprise AI platform API",
    version="0.1.0",
)

@app.post("/api/v1/llm")
async def ask_llm(prompt: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "qwen2.5:3b",
                "prompt": prompt,
                "stream": False,
            },
            timeout=120.0,
        )

    response.raise_for_status()
    return {"response": response.json()["response"]}


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



