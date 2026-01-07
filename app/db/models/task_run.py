from app.db.session import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

class TaskRun(Base):
    __tablename__ = "task_run"

    id = Column(Integer, primary_key=True)
    workflow_run_id = Column(Integer, ForeignKey("workflow_runs.id"))
    task_name = Column(String, nullable=False)
    status = Column(String, default="pending")
    error_message = Column(String, default="None")
    started_at = Column(DateTime)
    finished_at = Column(DateTime)