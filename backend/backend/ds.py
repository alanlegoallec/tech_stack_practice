import os
import secrets

from openai import OpenAI
from sqlalchemy import Column, Float, Integer
from sqlalchemy.orm import Session, declarative_base

Base = declarative_base()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class RandomNumber(Base):
    __tablename__ = "random_numbers"
    id = Column(Integer, primary_key=True, index=True)
    value = Column(Float, nullable=False)


def summarize_product(num1, num2, product):
    prompt = (
        "Write a short sentence summarizing the product of "
        f"{num1} and {num2}, which equals {product}."
    )
    try:
        response = client.chat.completions.create(
            model="gpt-4o",  # Or "gpt-4"
            messages=[{"role": "user", "content": prompt}],
            max_tokens=30,
            temperature=0.0,
        )
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        return f"Not AI: The product of {num1} and {num2} is {product}."


def multiply_with_random(number: float, db: Session):
    """Fetch a random multiplier from the DB and multiply it with the input."""
    random_numbers = db.query(RandomNumber).all()
    if not random_numbers:
        raise Exception("No random numbers found in the database.")
    random_number = secrets.choice(random_numbers).value
    result = number * random_number
    explanation = summarize_product(number, random_number, result)
    return result, random_number, explanation
