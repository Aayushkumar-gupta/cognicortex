from app.db.session import Base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey

def TaskRun(Base):
    __tablename__ = "task_run"

    id = Column(Integer, primary_key=True)
    workflow_run_id = Column(Integer, ForeignKey("workflow_run.id"))
    task_name = Column(String, nullable=False)
    status = Column(String, default="pending")
    started_at = Column(DateTime)
    finished_at = Column(DateTime)