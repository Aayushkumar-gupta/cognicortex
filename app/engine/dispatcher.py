from app.db.models.task_run import TaskRun

def dispatch_task(db, workflow_run, step):
    from app.workers.workflow_executor import execute_step

    existing_task = db.query(TaskRun).filter_by(
        workflow_run_id=workflow_run.id,
        workflow_step_id=step.id
    ).first()

    if existing_task:
        return

    task_run = TaskRun(
        workflow_run_id=workflow_run.id,
        task_name=step.name,
        status="QUEUED",
        workflow_step_id=step.id
    )

    db.add(task_run)
    db.commit()
    db.refresh(task_run)

    execute_step.delay(task_run.id)