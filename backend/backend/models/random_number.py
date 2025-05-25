from sqlalchemy import Column, Float, Integer

from backend.models.base import Base  # Or wherever your shared Base lives


class RandomNumber(Base):
    __tablename__ = "random_numbers"

    id = Column(Integer, primary_key=True, index=True)
    value = Column(Float, nullable=False)
