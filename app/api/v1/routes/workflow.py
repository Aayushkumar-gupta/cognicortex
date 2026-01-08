from fastapi import APIRouter
from app.workers.workflow_executor import execute_workflow
from app.workflows.workflow_test import WORKFLOW
from app.db.models.workflow_run import WorkflowRun
from app.db.models.task_run import TaskRun
from sqlalchemy.orm import Session
from fastapi import Depends
from app.db.session import get_db

router = APIRouter(prefix="/workflow", tags=['workflow'])

@router.post("/workflow")
def run_workflow(workflow_name: str):
    execute_workflow.delay(workflow_name)
    return {"status": "workflow started"}

@router.get("/list")
def list_workflows():

    workflows = []

    for workflow_name, tasks in WORKFLOW.items():
        workflows.append({
            "workflow_name": workflow_name,
            "tasks": tasks
        })
    
    return {"workflows": workflows}

@router.get("/monitor")
def monitor_workflows(db: Session = Depends(get_db)):

    workflow_runs = db.query(WorkflowRun).all()
    result = []

    for wf in workflow_runs:
        tasks = db.query(TaskRun).filter(TaskRun.workflow_run_id == wf.id).all()
        task_list = []
        for t in tasks:
            task_list.append({
                "task_name": t.task_name,
                "status": t.status,
                "started_at": t.started_at,
                "finished_at": t.finished_at,
                "error_message": t.error_message
            })

        result.append({
            "workflow_run_id": wf.id,
            "workflow_name": wf.workflow_name,
            "status": wf.status,
            "started_at": wf.started_at,
            "finished_at": wf.finished_at,
            "tasks": task_list
        })

    return {"workflow_runs": result}