from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(
        Integer, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False
    )
    name = Column(String, nullable=False)
    step_type = Column(String, nullable=False)
    config = Column(JSON, nullable=False)
    next_steps = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    workflow = relationship("Workflow", back_populates="steps")
