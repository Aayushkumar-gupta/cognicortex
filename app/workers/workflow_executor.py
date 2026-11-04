from datetime import datetime, timezone

from app.db.models.task_run import TaskRun
from app.db.session import SessionLocal
from app.engine.engine import run_workflow_engine
from app.workers.celery_app import celery_app


@celery_app.task(name="execute_workflow")
def execute_workflow(workflow_run_id: int):
    with SessionLocal() as db:
        run_workflow_engine(db, workflow_run_id)


@celery_app.task(name="execute_step")
def execute_step(task_run_id: int):
    with SessionLocal() as db:
        task_run = db.get(TaskRun, task_run_id)
        task_run.status = "RUNNING"
        task_run.started_at = datetime.now(timezone.utc)
        db.commit()

        try:
            execute_step_logic(task_run.workflow_step)
            task_run.status = "SUCCESS"
        except Exception as exc:
            task_run.status = "FAILED"
            task_run.error_message = str(exc)

        task_run.finished_at = datetime.now(timezone.utc)
        db.commit()

        run_workflow_engine(db, task_run.workflow_run_id)


def execute_step_logic(step):
    step_type = step.step_type

    if step_type == "action":
        return True

    if step_type == "trigger":
        return True

    return True
