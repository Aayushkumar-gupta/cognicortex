from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.security.jwt import get_current_user
from app.db.models.user import User
from app.db.models.workflow import Workflow
from app.db.models.workflow_step import WorkflowStep
from app.db.session import get_db
from app.schemas.workflow import WorkflowCreate, WorkflowResponse, WorkflowUpdate

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post("", response_model=WorkflowResponse)
def create_workflow(
    workflow: WorkflowCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    new_workflow = Workflow(
        name=workflow.name,
        description=workflow.description,
        owner_id=current_user.id,
    )
    db.add(new_workflow)
    db.commit()
    db.refresh(new_workflow)

    if workflow.steps:
        for step_data in workflow.steps:
            new_step = WorkflowStep(
                name=step_data.name,
                workflow_id=new_workflow.id,
                step_type=step_data.step_type,
                config=step_data.config,
                next_steps=step_data.next_steps,
            )
            db.add(new_step)
    db.commit()

    return new_workflow


@router.get("", response_model=list[WorkflowResponse])
def list_workflow(
    db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    workflow_list = (
        db.query(Workflow).filter(Workflow.owner_id == current_user.id).all()
    )

    return workflow_list


@router.get("/{workflow_id}", response_model=WorkflowResponse)
def get_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workflow = (
        db.query(Workflow)
        .filter(Workflow.owner_id == current_user.id, Workflow.id == workflow_id)
        .first()
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    return workflow


@router.put("/{workflow_id}", response_model=WorkflowResponse)
def update_workflow(
    workflow_id: int,
    workflow: WorkflowUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workflow_to_update = (
        db.query(Workflow)
        .filter(Workflow.owner_id == current_user.id, Workflow.id == workflow_id)
        .first()
    )

    if not workflow_to_update:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if workflow.name is not None:
        workflow_to_update.name = workflow.name
    if workflow.description is not None:
        workflow_to_update.description = workflow.description

    db.commit()
    db.refresh(workflow_to_update)

    return workflow_to_update


@router.delete("/{workflow_id}", response_model=WorkflowResponse)
def delete_workflow(
    workflow_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workflow = (
        db.query(Workflow)
        .filter(Workflow.owner_id == current_user.id, Workflow.id == workflow_id)
        .first()
    )

    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")

    db.delete(workflow)
    db.commit()

    return workflow
