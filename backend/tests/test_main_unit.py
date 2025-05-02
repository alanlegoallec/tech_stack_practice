"""Unit tests for the FastAPI application."""

import os

os.environ["UNIT_TESTS"] = "1"  # noqa: E402

from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.main import app, get_db


# Define the override function
def override_get_db():
    """Override the get_db dependency for testing."""
    yield MagicMock()


@pytest.fixture(autouse=True)
def db_override():
    """Override the get_db dependency for testing."""
    # Set the override before each test
    app.dependency_overrides[get_db] = override_get_db
    yield
    # Remove the override after each test
    app.dependency_overrides.pop(get_db, None)


client = TestClient(app)


def test_multiply_success(monkeypatch):
    """Test the multiply endpoint with a mocked database."""

    # Mock the multiply_with_random function to avoid DB dependency
    def fake_multiply_with_random(number, db):
        return number * 2, 2.0, "Multiplied by 2"

    monkeypatch.setattr("backend.main.multiply_with_random", fake_multiply_with_random)
    payload = {"number": 5.0}
    response = client.post("/multiply", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["result"] == 10.0
    assert data["multiplier"] == 2.0
    assert data["explanation"] == "Multiplied by 2"


def test_multiply_invalid_input():
    """Test the multiply endpoint with invalid input."""
    payload = {"number": "not_a_number"}
    response = client.post("/multiply", json=payload)
    assert response.status_code == 422  # Unprocessable Entity (validation error)
