from app.workers.celery_app import celery_app
import time
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models.task_run import TaskRun
from datetime import datetime

def run_task(task_name: str, workflow_run_id: int, duration: int = 2):
    db: Session = next(get_db())
    task = TaskRun(
        status="running",
        task_name=task_name,
        workflow_run_id=workflow_run_id,
        started_at=datetime.utcnow()
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    try:
        print(f"{task_name} started")
        time.sleep(duration)
        print(f"{task_name} finished")
        task.status = "finished"
        task.finished_at = datetime.utcnow()
        db.commit()
    except Exception as e:
        task.status = "failed"
        task.finished_at = datetime.utcnow()
        task.error_message = str(e)
        db.commit()
        raise


@celery_app.task(name="task_process_one")
def task_process_one(*args, **kwargs):
    run_task("task_process_one", kwargs.get("workflow_run_id"))

@celery_app.task(name="task_process_two")
def task_process_two(*args, **kwargs):
    run_task("task_process_two", kwargs.get("workflow_run_id"))

@celery_app.task(name="task_process_three")
def task_process_three(*args, **kwargs):
    run_task("task_process_three", kwargs.get("workflow_run_id"))
