"""Data science logic for the backend."""

import os
import secrets
import time

from sqlalchemy import Column, Float, Integer
from sqlalchemy.orm import Session, declarative_base

from backend.utils import get_secret, load_names_df, log_multiplication_to_s3

Base = declarative_base()

# Only initialize client if API key is present
api_key = get_secret(os.getenv("OPENAI_SECRET_NAME"))
client = None
if api_key:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)


class RandomNumber(Base):
    """Model for random numbers."""

    __tablename__ = "random_numbers"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(Float, nullable=False)


def summarize_product(num1, num2, product):
    """Use OpenAI API to summarize the product of two numbers."""
    prompt = (
        "Write a short sentence summarizing the product of "
        f"{num1} and {num2}, which equals {product}."
    )
    if client is None:
        return f"(No AI) The product of {num1} and {num2} is {product}."
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30,
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        return f"(Error) The product of {num1} and {num2} is {product}."


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
    explanation = summarize_product(number, multiplier, result)

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
