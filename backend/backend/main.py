"""API wrapper around backend logic."""

import logging
import os

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.ds import RandomNumber, multiply_with_random

# --- Configure logging ---
logging.basicConfig(level=logging.DEBUG)


# --- Database setup function ---
def setup_database():
    """Set up the database connection and session."""
    db_user = os.environ.get("POSTGRES_USER")
    db_password = os.environ.get("POSTGRES_PASSWORD")
    db_name = os.environ.get("POSTGRES_DB")
    db_host = os.environ.get("DB_HOST")
    db_port = os.environ.get("CONTAINER_DB_PORT")
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    print("DATABASE_URL:", DATABASE_URL)
    logging.info(f"DATABASE_URL: {DATABASE_URL}")

    # Check if any value is missing
    if not all([db_user, db_password, db_name, db_host, db_port]):
        missing_vars = [
            var
            for var, value in zip(
                [
                    "POSTGRES_USER",
                    "POSTGRES_PASSWORD",
                    "POSTGRES_DB",
                    "DB_HOST",
                    "CONTAINER_DB_PORT",
                ],
                [db_user, db_password, db_name, db_host, db_port],
            )
            if not value
        ]
        raise ValueError(f"Missing environment variables: {', '.join(missing_vars)}")

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


# --- Only initialize DB for non-unit-test runs ---
SessionLocal = None
if not os.environ.get("UNIT_TESTS"):
    SessionLocal = setup_database()


# --- Dependency for DB session ---
def get_db():
    """Dependency to get a database session."""
    if SessionLocal is None:
        # In unit tests, this will be overridden by dependency_overrides
        raise RuntimeError(
            "Database not initialized. This should be overridden in tests."
        )
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(debug=True)


# --- Global exception handler for logging all unhandled errors ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to log unhandled errors."""
    logging.exception(f"Unhandled error at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500, content={"detail": f"Internal Server Error: {exc}"}
    )


class MultiplyRequest(BaseModel):
    """Request model for the multiply endpoint."""

    number: float


class MultiplyResponse(BaseModel):
    """Response model for the multiply endpoint."""

    result: float
    multiplier: float
    explanation: str


@app.post("/multiply", response_model=MultiplyResponse)
def multiply(request: MultiplyRequest, db: Session = Depends(get_db)):
    """Multiply a number by a random number from the database."""
    print("Random numbers in DB:", db.query(RandomNumber).all())
    try:
        result, multiplier, explanation = multiply_with_random(request.number, db)
        return MultiplyResponse(
            result=result, multiplier=multiplier, explanation=explanation
        )
    except Exception as e:
        logging.exception(f"Error in /multiply endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
