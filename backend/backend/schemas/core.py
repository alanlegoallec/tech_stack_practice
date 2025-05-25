# ---------- Pydantic Models ---------------------------------------------------
from pydantic import BaseModel


class MultiplyRequest(BaseModel):
    number: float


class MultiplyResponse(BaseModel):
    result: float
    multiplier: float
    explanation: str


class HealthResponse(BaseModel):
    status: str
