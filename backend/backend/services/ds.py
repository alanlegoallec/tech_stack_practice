"""Data science logic for the backend."""

import logging
import os
import secrets
import time

from sqlalchemy import Column, Float, Integer
from sqlalchemy.orm import Session, declarative_base

from backend.core.utils import get_secret, load_names_df, log_multiplication_to_s3
from backend.models.random_number import RandomNumber
from backend.services.llm import summarize_product

# Only initialize client if API key is present
api_key = get_secret(os.getenv("OPENAI_SECRET_NAME"))
client = None
if api_key:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)


def multiply_with_random(number: float, db: Session = None, client_ip: str = "unknown"):
    start = time.time()

    if os.getenv("BYPASS_DB", "").lower() == "true":
        multiplier = 6
    else:
        if db is None:
            raise ValueError("No DB session provided.")
        records = db.query(RandomNumber).all()
        if not records:
            raise ValueError("No random numbers found in the database.")
        multiplier = secrets.choice(records).value

    result = number * multiplier
    explanation = summarize_product(number, multiplier, result, client)

    try:
        df = load_names_df()
        closest = df.iloc[(df["number"] - result).abs().argmin()]
        name = closest["name"]
        explanation += f" Closest name: {name}"

    except Exception as e:
        name = None
        explanation += f" (Could not match name from S3: {e})"

    latency = (time.time() - start) * 1000
    try:
        log_multiplication_to_s3(
            user_input=number,
            multiplier=multiplier,
            product=result,
            name=name,
            explanation=explanation,
            latency_ms=latency,
            client_ip=client_ip,
        )
    except Exception as e:
        logging.warning(f"⚠️ Logging to S3 failed: {e}")

    return result, multiplier, explanation
