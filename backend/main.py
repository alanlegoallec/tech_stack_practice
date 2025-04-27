import os
from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.backend import Base, RandomNumber, multiply_with_random

# Database setup
db_user = os.environ.get("POSTGRES_USER")
db_password = os.environ.get("POSTGRES_PASSWORD")
db_name = os.environ.get("POSTGRES_DB")
db_host = os.environ.get("DB_HOST", "db")
db_port = os.environ.get("DB_PORT", 5432)
DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

class MultiplyRequest(BaseModel):
    number: float

class MultiplyResponse(BaseModel):
    result: float
    multiplier: float
    explanation: str

@app.post("/multiply", response_model=MultiplyResponse)
def multiply(request: MultiplyRequest, db: Session = Depends(get_db)):
    try:
        result, multiplier, explanation = multiply_with_random(request.number, db)
        return MultiplyResponse(result=result, multiplier=multiplier, explanation=explanation)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
