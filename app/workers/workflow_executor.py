from app.workers.celery_app import celery_app
from app.workflows.workflow_test import WORKFLOW

@celery_app.task(name="execute_workflow")
def execute_workflow(workflow_name: str, workflow_run_id: int):
    tasks = WORKFLOW.get(workflow_name)

    if not tasks:
        raise ValueError("Workflow not found")
    
    chain_tasks = []

    for task_name in tasks:
        chain_tasks.append(celery_app.signature(task_name))
    

    from celery import chain
    chain(*chain_tasks).delay()