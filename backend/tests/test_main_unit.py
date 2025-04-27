import os
os.environ["UNIT_TESTS"] = "1"
import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from backend.backend.main import app, get_db

# Define the override function
def override_get_db():
    yield MagicMock()

@pytest.fixture(autouse=True)
def db_override():
    # Set the override before each test
    app.dependency_overrides[get_db] = override_get_db
    yield
    # Remove the override after each test
    app.dependency_overrides.pop(get_db, None)

client = TestClient(app)

def test_multiply_success(monkeypatch):
    # Mock the multiply_with_random function to avoid DB dependency
    def fake_multiply_with_random(number, db):
        return number * 2, 2.0, "Multiplied by 2"

    monkeypatch.setattr("backend.backend.main.multiply_with_random", fake_multiply_with_random)
    payload = {"number": 5.0}
    response = client.post("/multiply", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 10.0
    assert data["multiplier"] == 2.0
    assert data["explanation"] == "Multiplied by 2"

def test_multiply_invalid_input():
    payload = {"number": "not_a_number"}
    response = client.post("/multiply", json=payload)
    assert response.status_code == 422  # Unprocessable Entity (validation error)
