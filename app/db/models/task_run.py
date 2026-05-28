from app.db.session import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

class TaskRun(Base):
    __tablename__ = "task_runs"

    id = Column(Integer, primary_key=True)
    workflow_run_id = Column(Integer, ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False)
    task_name = Column(String, nullable=False)
    status = Column(String, default="pending")
    error_message = Column(String, default="None")
    started_at = Column(DateTime)
    finished_at = Column(DateTime)
    workflow_run = relationship("WorkflowRun", back_populates="task_runs")
    workflow_step = relationship("WorkflowStep")
    workflow_run_id = Column(Integer, ForeignKey("workflow_runs.id", ondelete="CASCADE"), nullable=False)
    workflow_step_id = Column(Integer, ForeignKey("workflow_steps.id", ondelete="CASCADE"), nullable=False)