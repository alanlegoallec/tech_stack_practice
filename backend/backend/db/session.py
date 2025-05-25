# backend/backend/db.py
import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.utils import get_secret


def _build_url():
    user = os.getenv("POSTGRES_USER")
    pwd = get_secret(os.getenv("POSTGRES_SECRET_NAME"))
    name = os.getenv("POSTGRES_DB")
    host = os.getenv("DB_HOST")
    port = os.getenv("CONTAINER_DB_PORT")
    return f"postgresql://{user}:{pwd}@{host}:{port}/{name}?sslmode=require"


engine = create_engine(_build_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
