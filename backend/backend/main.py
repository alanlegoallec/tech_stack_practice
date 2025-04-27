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
    db_user = os.environ.get("POSTGRES_USER")
    db_password = os.environ.get("POSTGRES_PASSWORD")
    db_name = os.environ.get("POSTGRES_DB")
    db_host = os.environ.get("DB_HOST", "db")
    db_port = os.environ.get("DB_PORT", 5432)
    DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    print("DATABASE_URL:", DATABASE_URL)
    logging.info(f"DATABASE_URL: {DATABASE_URL}")

    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


# --- Only initialize DB for non-unit-test runs ---
SessionLocal = None
if not os.environ.get("UNIT_TESTS"):
    SessionLocal = setup_database()


# --- Dependency for DB session ---
def get_db():
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
    logging.exception(f"Unhandled error at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500, content={"detail": f"Internal Server Error: {exc}"}
    )


class MultiplyRequest(BaseModel):
    number: float


class MultiplyResponse(BaseModel):
    result: float
    multiplier: float
    explanation: str


@app.post("/multiply", response_model=MultiplyResponse)
def multiply(request: MultiplyRequest, db: Session = Depends(get_db)):
    print("Random numbers in DB:", db.query(RandomNumber).all())
    try:
        result, multiplier, explanation = multiply_with_random(request.number, db)
        return MultiplyResponse(
            result=result, multiplier=multiplier, explanation=explanation
        )
    except Exception as e:
        logging.exception(f"Error in /multiply endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))
