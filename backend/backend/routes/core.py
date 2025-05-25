import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.db import get_db
from backend.ds import RandomNumber, multiply_with_random

router = APIRouter(prefix="", tags=["core"])

# ---------- Pydantic Models ---------------------------------------------------


class MultiplyRequest(BaseModel):
    number: float


class MultiplyResponse(BaseModel):
    result: float
    multiplier: float
    explanation: str


# ---------- Routes ------------------------------------------------------------


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/multiply", response_model=MultiplyResponse)
def multiply(
    request: Request,
    request_data: MultiplyRequest,
    db: Session = Depends(get_db),
):
    """Multiply a number by a random number from the database and log to S3."""
    try:
        client_ip = request.client.host if request.client else "unknown"
    except Exception:
        client_ip = "unknown"

    logging.info(f"Received request from {client_ip} with number={request_data.number}")

    try:
        result, multiplier, explanation = multiply_with_random(
            request_data.number,
            db=db,
            client_ip=client_ip,
        )
        return MultiplyResponse(
            result=result,
            multiplier=multiplier,
            explanation=explanation,
        )
    except Exception as e:
        logging.exception("Error in /multiply endpoint")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/debug/db")
def check_db(db: Session = Depends(get_db)):
    """Debug endpoint: return all random number values from DB."""
    records = db.query(RandomNumber).all()
    return [r.value for r in records]
