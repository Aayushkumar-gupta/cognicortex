from app.workers.celery_app import celery_app
from app.workflows.workflow_test import WORKFLOW
from app.db.models.workflow_run import WorkflowRun
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import get_db
from celery import chain
from app.engine.engine import run_workflow_engine
from app.db.models.workflow import Workflow
from app.db.models.task_run import TaskRun
from app.workflows.models import WorkflowStep


@celery_app.task(name="mark_workflow_finished")
def mark_workflow_finished(workflow_run_id: int):
    db: Session = next(get_db())

    workflow_run = db.query(WorkflowRun).filter_by(id = workflow_run_id).first()

    if not workflow_run:
        return
    
    workflow_run.status = "finished"
    workflow_run.finished_at = datetime.utcnow()
    db.commit()

@celery_app.task(name="execute_workflow")
def execute_workflow(workflow_id: int):
    db: Session = next(get_db())

    workflow = db.query(Workflow).get(workflow_id)
    if not workflow:
        raise ValueError("Workflow not found")

    workflow_run = WorkflowRun(
        workflow_id=workflow.id,
        workflow_name=workflow.name,
        status="RUNNING",
        started_at=datetime.utcnow()
    )

    db.add(workflow_run)
    db.commit()
    db.refresh(workflow_run)

    run_workflow_engine(db, workflow_run.id)

@celery_app.task(name="execute_step")
def execute_step(task_run_id: int):
    db: Session = next(get_db())

    task_run = db.query(TaskRun).get(task_run_id)
    step = task_run.workflow_step

    try:
        execute_step_logic(step)
        task_run.status = "SUCCESS"
    except Exception:
        task_run.status = "FAILED"

    db.commit()

    run_workflow_engine(db, task_run.workflow_run_id)

def execute_step_logic(step):
    step_type = step.step_type

    if step_type == "action":
        return True

    if step_type == "trigger":
        return True

    return True
