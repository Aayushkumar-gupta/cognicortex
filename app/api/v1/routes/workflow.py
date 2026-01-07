from fastapi import APIRouter
from app.workers.workflow_executor import execute_workflow

router = APIRouter(prefix="/workflow", tags=['workflow'])

@router.post("/workflow")
def run_workflow(workflow_name: str):
    execute_workflow.delay(workflow_name, workflow_run_id=1)
    return {"status": "workflow started"}