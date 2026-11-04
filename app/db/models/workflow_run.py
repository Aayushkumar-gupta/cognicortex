from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True)
    workflow_id = Column(
        Integer, ForeignKey("workflows.id", ondelete="CASCADE"), nullable=False
    )
    workflow_name = Column(String, nullable=False)
    status = Column(String, default="pending")
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    workflow = relationship("Workflow", back_populates="workflow_runs")
    task_runs = relationship(
        "TaskRun", back_populates="workflow_run", cascade="all, delete-orphan"
    )
