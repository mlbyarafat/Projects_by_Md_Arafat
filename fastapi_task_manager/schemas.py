from pydantic import BaseModel, EmailStr
from typing import Optional
import datetime

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        orm_mode = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_done: Optional[bool] = False
    due_date: Optional[datetime.datetime] = None

class TaskCreate(TaskBase):
    pass

class TaskUpdate(TaskBase):
    pass

class TaskOut(TaskBase):
    id: int
    owner_id: Optional[int]
    created_at: datetime.datetime

    class Config:
        orm_mode = True