
from fastapi.testclient import TestClient

from backend.main import app

from uuid import uuid4


client = TestClient(app)


def test_create_customer():
    email = f"test-{uuid4()}@example.com"

    response = client.post(
        "/api/v1/customers",
        json={
            "name": "Test Customer",
            "email": email,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["id"] is not None
    assert data["name"] == "Test Customer"
    assert data["email"] == email



def test_create_customer_with_duplicate_email():
    email = f"{uuid4()}@example.com"

    first_response = client.post(
        "/api/v1/customers",
        json={
            "name": "First Customer",
            "email": email,
        },
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/customers",
        json={
            "name": "Second Customer",
            "email": email,
        },
    )

    assert second_response.status_code == 409
    assert second_response.json()["detail"] == (
        "A customer with this email already exists."
    )
