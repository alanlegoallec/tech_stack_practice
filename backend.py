# backend.py

from flask_sqlalchemy import SQLAlchemy
import random
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

db = SQLAlchemy()

class RandomNumber(db.Model):
    __tablename__ = 'random_numbers'
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)

def summarize_product(num1, num2, product):
    # NEW: Call OpenAI to generate a summary sentence
    prompt = f"Write a short sentence summarizing the product of {num1} and {num2}, which equals {product}."
    try:
        response = client.chat.completions.create(model="gpt-4o",  # Or "gpt-4" if you have access
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=30,
        temperature=0.0)
        summary = response.choices[0].message.content.strip()
        return summary
    except Exception as e:
        print(f"OpenAI API call failed: {e}")
        return f"Not AI: The product of {num1} and {num2} is {product}."

def multiply_with_random(number):
    """Fetch a random multiplier from the DB and multiply it with the input."""
    random_numbers = RandomNumber.query.all()
    if not random_numbers:
        raise Exception("No random numbers found in the database.")
    random_number = random.choice(random_numbers).value
    result = number * random_number
    explanation = summarize_product(number, random_number, result)
    return result, random_number, explanation
