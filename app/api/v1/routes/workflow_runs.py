from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.core.security.jwt import get_current_user
from app.db.models.user import User
from app.db.models.workflow import Workflow
from app.db.models.workflow_run import WorkflowRun
from app.db.session import get_db
from app.workers.workflow_executor import execute_workflow

router = APIRouter(prefix="/workflow_runs", tags=['workflow_runs'])


@router.post("", status_code=status.HTTP_202_ACCEPTED)
def run_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    workflow = (
        db.query(Workflow)
        .filter(Workflow.id == workflow_id, Workflow.owner_id == current_user.id)
        .first()
    )

    if not workflow:
        raise HTTPException(
            status_code=404,
            detail="Workflow not found"
        )

    workflow_run = WorkflowRun(
        workflow_id=workflow.id,
        workflow_name=workflow.name,
        status="RUNNING",
        started_at=datetime.now(timezone.utc)
    )
    db.add(workflow_run)
    db.commit()
    db.refresh(workflow_run)

    execute_workflow.delay(workflow_run.id)
    return {"workflow_run_id": workflow_run.id, "status": workflow_run.status}


@router.get("/{workflow_run_id}")
def monitor_workflow_run(
    workflow_run_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    workflow_run = (
        db.query(WorkflowRun)
        .join(WorkflowRun.workflow)
        .options(joinedload(WorkflowRun.task_runs))
        .filter(
            WorkflowRun.id == workflow_run_id,
            Workflow.owner_id == current_user.id
        )
        .first()
    )

    if not workflow_run:
        raise HTTPException(
            status_code=404,
            detail="Workflow run not found"
        )

    tasks = workflow_run.task_runs

    total_tasks = len(tasks)

    completed_tasks = sum(
        1 for t in tasks if t.status == "SUCCESS"
    )

    running_tasks = sum(
        1 for t in tasks if t.status in ("RUNNING", "running")
    )

    failed_tasks = sum(
        1 for t in tasks if t.status == "FAILED"
    )

    pending_tasks = sum(
        1 for t in tasks if t.status in ("QUEUED", "queued", "pending")
    )

    task_details = []

    for t in tasks:

        duration = None

        if t.started_at and t.finished_at:
            duration = (
                t.finished_at - t.started_at
            ).total_seconds()

        task_details.append({
            "task_name": t.task_name,
            "status": t.status,
            "started_at": t.started_at,
            "finished_at": t.finished_at,
            "duration_seconds": duration,
            "error_message": t.error_message
        })

    return {
        "workflow_run_id": workflow_run.id,
        "workflow_name": workflow_run.workflow_name,
        "status": workflow_run.status,
        "started_at": workflow_run.started_at,
        "finished_at": workflow_run.finished_at,

        "summary": {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "running_tasks": running_tasks,
            "failed_tasks": failed_tasks,
            "pending_tasks": pending_tasks
        },

        "tasks": task_details
    }
