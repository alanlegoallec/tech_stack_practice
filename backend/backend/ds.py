"""Data science logic for the backend."""

import os
import secrets

from sqlalchemy import Column, Float, Integer
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()

# Only initialize client if API key is present
api_key = os.getenv("OPENAI_API_KEY")
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


def multiply_with_random(number: float, db: Session = None):
    """Fetch a random multiplier and multiply it with the input."""
    # Bypass DB if environment variable is set
    if os.getenv("BYPASS_DB", "").lower() == "true":
        multiplier = 1.23  # hardcoded fallback
    else:
        if db is None:
            raise Exception("No DB session provided.")
        records = db.query(RandomNumber).all()
        if not records:
            raise Exception("No random numbers found in the database.")
        multiplier = secrets.choice(records).value

    result = number * multiplier
    explanation = summarize_product(number, multiplier, result)
    return result, multiplier, explanation
