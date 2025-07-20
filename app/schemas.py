from pydantic import BaseModel
from typing import Optional


class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None


class TaskCreate(TaskBase):
    pass


class TaskUpdate(TaskBase):
    completed: bool


class TaskOut(TaskBase):
    id: int
    completed: bool

    class Config:
        orm_mode = True
