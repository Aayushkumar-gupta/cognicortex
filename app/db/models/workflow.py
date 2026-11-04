from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    owner_id = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    steps = relationship(
        "WorkflowStep", back_populates="workflow", cascade="all, delete-orphan"
    )
    workflow_runs = relationship(
        "WorkflowRun", back_populates="workflow", cascade="all, delete-orphan"
    )
