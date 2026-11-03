from datetime import datetime

from sqlalchemy.orm import Session

from app.db.models.task_run import TaskRun
from app.db.models.workflow_run import WorkflowRun
from app.engine.dispatcher import dispatch_task


def run_workflow_engine(db: Session, workflow_run_id: int):
    workflow_run = db.get(WorkflowRun, workflow_run_id)

    if not workflow_run:
        raise Exception("WorkflowRun not found")

    steps = workflow_run.workflow.steps

    for step in steps:

        existing_task = (
            db.query(TaskRun)
            .filter(
                TaskRun.workflow_run_id == workflow_run.id,
                TaskRun.workflow_step_id == step.id
            )
            .first()
        )

        if existing_task:
            continue

        can_run = True

        for parent_step in steps:
            if parent_step.next_steps and step.id in parent_step.next_steps:

                parent_task = (
                    db.query(TaskRun)
                    .filter(
                        TaskRun.workflow_run_id == workflow_run.id,
                        TaskRun.workflow_step_id == parent_step.id,
                        TaskRun.status == "SUCCESS"
                    )
                    .first()
                )

                if not parent_task:
                    can_run = False
                    break

        if can_run:
            dispatch_task(db, workflow_run, step)

    active_tasks_count = (
        db.query(TaskRun)
        .filter(
            TaskRun.workflow_run_id == workflow_run.id,
            TaskRun.status.in_(["QUEUED", "RUNNING"])
        )
        .count()
    )

    if active_tasks_count == 0:
        failed_tasks_count = (
            db.query(TaskRun)
            .filter(
                TaskRun.workflow_run_id == workflow_run.id,
                TaskRun.status == "FAILED"
            )
            .count()
        )

        workflow_run.status = "FAILED" if failed_tasks_count > 0 else "FINISHED"
        workflow_run.finished_at = datetime.utcnow()
        db.commit()
