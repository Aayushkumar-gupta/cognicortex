from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.db.session import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    status = Column(String, default='pending')
    owner_id = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=DateTime.utcnow)
    updated_at = Column(DateTime, default=DateTime.utcnow, onupdate=DateTime.utcnow)
