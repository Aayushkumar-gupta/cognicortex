from typing import Any

from pydantic import BaseModel, ConfigDict


class WorkflowStepBase(BaseModel):
    name: str
    step_type: str
    config: dict[str, Any]
    next_steps: list[int] | None = None


class WorkflowStepCreate(WorkflowStepBase):
    pass


class WorkflowStepResponse(WorkflowStepBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class WorkflowBase(BaseModel):
    name: str
    description: str | None = None


class WorkflowCreate(WorkflowBase):
    steps: list[WorkflowStepCreate] | None = []


class WorkflowResponse(WorkflowBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    steps: list[WorkflowStepResponse] = []


class WorkflowUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
