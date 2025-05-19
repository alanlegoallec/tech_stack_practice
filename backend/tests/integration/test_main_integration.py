"""Tests for the FastAPI app using a real PostgreSQL database."""

import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.ds import Base, RandomNumber
from backend.main import app, get_db

# Use the same DB URL as your app (from env vars)
db_user = os.environ["POSTGRES_USER"]
db_password = os.environ["POSTGRES_PASSWORD"]
db_name = os.environ["POSTGRES_DB_TEST"]
db_host = os.environ.get("DB_HOST")
db_port = os.environ.get("CONTAINER_DB_PORT")
DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?sslmode=require"

engine = create_engine(DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables (if not already created)
Base.metadata.create_all(bind=engine)


# Dependency override for tests
def override_get_db():
    """Override the get_db dependency for testing."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    """Set up the test database and clean up after tests."""
    # Clean up and insert a known random number into the test DB
    db = TestingSessionLocal()
    db.query(RandomNumber).delete()  # Clean table for repeatable tests
    db.add(RandomNumber(value=3.0))
    db.commit()
    db.close()
    yield
    # Optional: Clean up after tests
    db = TestingSessionLocal()
    db.query(RandomNumber).delete()
    db.commit()
    db.close()


def test_multiply_with_real_db():
    """Test the multiply_with_random function with a real database."""
    payload = {"number": 5.0}
    response = client.post("/multiply", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["multiplier"] == 3.0
    assert data["result"] == 15.0
    assert "explanation" in data
