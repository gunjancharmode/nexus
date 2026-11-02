
import os

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from backend.main import app, get_db
from backend.models import Base


TEST_DATABASE_URL = os.getenv("NEXUS_TEST_DATABASE_URL")

if not TEST_DATABASE_URL:
    raise RuntimeError(
        "NEXUS_TEST_DATABASE_URL is missing from the root .env file."
    )

test_engine = create_engine(
    TEST_DATABASE_URL,
    pool_pre_ping=True,
)

TestingSessionLocal = sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
)


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client():
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()

def test_list_customers_returns_empty_list_when_no_customers(client):
    response = client.get("/api/v1/customers")

    assert response.status_code == 200
    assert response.json() == []


def test_list_customers_valid_pagination(client):
    response = client.get("/api/v1/customers?limit=2&offset=0")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_list_customers_rejects_limit_above_maximum(client):
    response = client.get("/api/v1/customers?limit=101")

    assert response.status_code == 422


def test_list_customers_rejects_zero_limit(client):
    response = client.get("/api/v1/customers?limit=0")

    assert response.status_code == 422


def test_list_customers_rejects_negative_offset(client):
    response = client.get("/api/v1/customers?offset=-1")

    assert response.status_code == 422

def test_list_customers_accepts_maximum_limit(client):
    response = client.get("/api/v1/customers?limit=100")

    assert response.status_code == 200
    assert isinstance(response.json(), list)



def test_list_customers_pagination_returns_correct_records(client):
    client.post(
        "/api/v1/customers",
        json={"name": "Customer A", "email": "customer.a@example.com"},
    )
    client.post(
        "/api/v1/customers",
        json={"name": "Customer B", "email": "customer.b@example.com"},
    )
    client.post(
        "/api/v1/customers",
        json={"name": "Customer C", "email": "customer.c@example.com"},
    )

    response = client.get("/api/v1/customers?limit=2&offset=1")

    assert response.status_code == 200

    customers = response.json()

    assert len(customers) == 2
    assert customers[0]["name"] == "Customer B"
    assert customers[1]["name"] == "Customer C"

def test_list_customers_returns_sucess(client):
    response = client.get("/api/v1/customers")

    assert response.status_code == 200
    assert isinstance(response.json(),list)


