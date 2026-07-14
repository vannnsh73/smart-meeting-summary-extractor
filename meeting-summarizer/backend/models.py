"""
SQLAlchemy ORM models.
"""
from sqlalchemy import Column, Integer, String, Text, JSON, DateTime
from sqlalchemy.sql import func
from database import Base

class Meeting(Base):
    """
    Meeting model for storing transcriptions and summaries.
    """
    __tablename__ = "meetings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, default="Untitled Meeting")
    transcript = Column(Text, nullable=False)
    summary = Column(Text, nullable=False)
    decisions = Column(JSON, nullable=False)
    action_items = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
