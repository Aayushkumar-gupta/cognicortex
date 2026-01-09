from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.session import Base
from app.db.session import get_db
from app.db.models.workflow import Workflow
from app.workflows.models import WorkflowStep
from app.workflows.schemas import WorkflowBase, WorkflowCreate, WorkflowResponse
from app.core.security.jwt import get_current_user
from app.db.models.user import User


router = APIRouter(prefix="/workflow_crud", tags=["workflow_crud"])

@router.post("/create_workflow", response_model=WorkflowResponse)
def create_workflow(workflow: WorkflowCreate, 
    db: Session = Depends(get_db), 
    currentuser: User = Depends(get_current_user)):


    new_workflow = Workflow(
        name = workflow.name,
        description = workflow.description,
        owner_id = currentuser.id,
    )
    db.add(new_workflow)
    db.commit()
    db.refresh(new_workflow)

    if workflow.steps:
        for step_data in workflow.steps:
            new_step = WorkflowStep(
                name = step_data.name,
                workflow_id = new_workflow.id,
                step_type = step_data.step_type,
                config = step_data.config,
                next_steps = step_data.next_steps,
            )
            db.add(new_step)
    db.commit()


    return new_workflow
