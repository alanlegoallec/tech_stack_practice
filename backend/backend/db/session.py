# backend/backend/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.core.utils import get_secret_value, require_env_var


def _build_url():
    user = require_env_var("POSTGRES_USER")
    pwd = get_secret_value(require_env_var("POSTGRES_SECRET_NAME"))
    name = require_env_var("POSTGRES_DB")
    host = require_env_var("DB_HOST")
    port = require_env_var("CONTAINER_DB_PORT")
    return f"postgresql://{user}:{pwd}@{host}:{port}/{name}?sslmode=require"


engine = create_engine(_build_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
