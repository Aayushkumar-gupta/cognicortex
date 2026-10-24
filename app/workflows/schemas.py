from pydantic import BaseModel, ConfigDict
from typing import List, Optional, Dict, Any


class WorkflowStepBase(BaseModel):
    name: str
    step_type: str
    config: Dict[str, Any]
    next_steps: Optional[List[int]] = None


class WorkflowStepCreate(WorkflowStepBase):
    pass


class WorkflowStepResponse(WorkflowStepBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None


class WorkflowCreate(WorkflowBase):
    steps: Optional[List[WorkflowStepCreate]] = []


class WorkflowResponse(WorkflowBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    steps: List[WorkflowStepResponse] = []


class WorkflowUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
