from app.db.session import Base
from sqlalchemy import Column, Integer, String, DateTime

def WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id = Column(Integer, primary_key=True)
    workflow_name = Column(String, nullable=False)
    status = Column(String, default="pending")
    stated_at = Column(DateTime)
    finished_at = Column(DateTime)
