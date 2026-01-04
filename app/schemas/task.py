from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CreateTask(BaseModel):
    name: str
    description: str

class ReadTask(BaseModel):
    id: int
    name: str
    status: str
    created_at: datetime
    updated_at: datetime

    class config:
        orm_mode = True

class UpdateTask(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None