"""API wrapper around backend logic."""

import logging
import os

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# --- Configure logging ---
logging.basicConfig(level=logging.DEBUG)

app = FastAPI(debug=True)


class MultiplyRequest(BaseModel):
    """Request model for the multiply endpoint."""

    number: float


class MultiplyResponse(BaseModel):
    """Response model for the multiply endpoint."""

    result: float
    multiplier: float
    explanation: str


@app.get("/")
def root():
    return {"message": "API is running"}


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/multiply", response_model=MultiplyResponse)
def multiply(request: MultiplyRequest):
    """Multiply a number by 2.5 (no database dependency)."""
    multiplier = 2.5
    result = request.number * multiplier
    explanation = f"Multiplied {request.number} by {multiplier}"
    return MultiplyResponse(
        result=result, multiplier=multiplier, explanation=explanation
    )


# --- Global exception handler for logging all unhandled errors ---
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler to log unhandled errors."""
    logging.exception(f"Unhandled error at {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500, content={"detail": f"500 Internal Server Error: {exc}"}
    )
