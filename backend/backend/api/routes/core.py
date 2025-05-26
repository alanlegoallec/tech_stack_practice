import logging
from typing import Any

from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from backend.core.security import get_current_user
from backend.db.session import get_db
from backend.models.user import User
from backend.schemas.core import HealthResponse, MultiplyRequest, MultiplyResponse
from backend.services.ds import multiply_with_random

router = APIRouter(prefix="", tags=["core"])


# ---------- Routes ------------------------------------------------------------


@router.get("/health", response_model=HealthResponse)
def health_check():
    return {"status": "ok"}


@router.post("/multiply", response_model=MultiplyResponse)
def multiply(
    request: Request,
    request_data: MultiplyRequest = Body(...),
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
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
