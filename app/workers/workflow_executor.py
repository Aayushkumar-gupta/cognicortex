from app.workers.celery_app import celery_app
from app.workflows.workflow_test import WORKFLOW
from app.db.models.workflow_run import WorkflowRun
from datetime import datetime
from sqlalchemy.orm import Session
from app.db.session import get_db
from celery import chain

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
def execute_workflow(workflow_name: str):
    tasks = WORKFLOW.get(workflow_name)

    if not tasks:
        raise ValueError("Workflow not found")
    
    db: Session = next(get_db())
    
    new_workflow = WorkflowRun(
        workflow_name = workflow_name,
        status = "pending",
        started_at = datetime.utcnow()
    )

    db.add(new_workflow)
    db.commit()
    db.refresh(new_workflow)

    workflow_run_id = new_workflow.id

    chain_tasks = []

    for task_name in tasks:
        chain_tasks.append(celery_app.signature(task_name, kwargs={"workflow_run_id": workflow_run_id}))



    workflow_chain = chain(*chain_tasks) | mark_workflow_finished.si(workflow_run_id)
    workflow_chain.apply_async()
