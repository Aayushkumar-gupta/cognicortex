from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.task import CreateTask, ReadTask, UpdateTask
from app.db.models.user import User
from app.db.models.task import Task
from app.core.security.jwt import get_current_user

router = APIRouter(prefix="/task", tags=["task"])

@router.post("/createTask", response_model=ReadTask)
def create_task(
    task: CreateTask,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    new_task = Task(
        name = task.name,
        description = task.description,
        owner_id = current_user.id,
        status = "pending"
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return new_task


@router.get("/getTask", response_model=ReadTask)
def list_task(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    tasks = db.query(Task).filter(Task.owner_id == current_user.id).all()
    return tasks


@router.put("/updateTask/{task_id}", response_model=ReadTask)
def update_task(
    task_id: int,
    task: UpdateTask,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
    ):

    task_to_update = db.query(Task).filter(
        Task.owner_id == current_user.id, 
        Task.id == task_id
        ).first()

    if not task_to_update:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.name is not None:
        task_to_update.name = task.name
    if task.description is not None:
        task_to_update.description = task.description
    
    db.commit()
    db.refresh(task_to_update)

    return task_to_update

@router.delete("/delete/{task_id}", response_model=ReadTask)
def delete_task(
    task_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    task_to_delete = db.query(Task).filter(
        Task.owner_id == current_user.id,
        Task.id == task_id
    ).first()

    if not task_to_delete:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task_to_delete)
    db.commit()

    return task_to_delete
    