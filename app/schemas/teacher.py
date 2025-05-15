from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class TeacherBase(BaseModel):
    username: str
    email: EmailStr
    name: str
    title: Optional[str] = None

class TeacherCreate(TeacherBase):
    password: str

class Teacher(TeacherBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 