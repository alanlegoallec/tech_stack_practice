"""API wrapper around backend logic."""

import logging
import os

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.ds import RandomNumber, multiply_with_random

# --- Logging ---
logging.basicConfig(level=logging.DEBUG)


# --- DB Setup ---
def setup_database():
    db_user = os.getenv("POSTGRES_USER")
    db_password = os.getenv("POSTGRES_PASSWORD")
    db_name = os.getenv("POSTGRES_DB")
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("CONTAINER_DB_PORT")
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    logging.info(f"DATABASE_URL: {DATABASE_URL}")

    if not all([db_user, db_password, db_name, db_host, db_port]):
        raise ValueError("Missing required DB environment variables.")

    engine = create_engine(DATABASE_URL)
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


SessionLocal = None
if not os.getenv("UNIT_TESTS") and os.getenv("BYPASS_DB", "").lower() != "true":
    SessionLocal = setup_database()


def get_db():
    if SessionLocal is None:
        raise RuntimeError("DB not initialized. Use BYPASS_DB=true for fallback.")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


app = FastAPI(debug=True)


# --- Global Exception Handler ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.exception(f"Unhandled error at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500, content={"detail": f"Internal Server Error: {exc}"}
    )


# --- Models ---
class MultiplyRequest(BaseModel):
    number: float


class MultiplyResponse(BaseModel):
    result: float
    multiplier: float
    explanation: str


# --- Endpoint ---
@app.post("/multiply", response_model=MultiplyResponse)
def multiply(
    request: MultiplyRequest, db: Session = Depends(get_db) if SessionLocal else None
):
    try:
        result, multiplier, explanation = multiply_with_random(request.number, db)
        return MultiplyResponse(
            result=result, multiplier=multiplier, explanation=explanation
        )
    except Exception as e:
        logging.exception(f"Error in /multiply endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
