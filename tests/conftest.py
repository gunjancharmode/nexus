
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
    join_transaction_mode="create_savepoint",
)


@pytest.fixture(scope="session", autouse=True)
def create_test_tables():
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture()
def client():
    connection = test_engine.connect()
    transaction = connection.begin()

    def override_get_db():
        db = TestingSessionLocal(bind=connection)
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        transaction.rollback()
        connection.close()
