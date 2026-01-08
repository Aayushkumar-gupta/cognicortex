from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class WorkflowStepBase(BaseModel):
    name: str
    step_type: str
    config: Dict[str, Any]
    next_steps: Optional[List[int]] = None

class WorkflowStepCreate(WorkflowStepBase):
    workflow_id: int

class WorkflowStepResponse(WorkflowStepBase):
    id: int

    class Config:
        orm_mode = True

class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowResponse(WorkflowBase):
    id: int
    steps: List[WorkflowStepResponse] = []

    class Config:
        orm_mode = True