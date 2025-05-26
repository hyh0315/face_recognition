from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class TeacherBase(BaseModel):
    username: str
    email: EmailStr
    name: str
    title: str
    department: str

class TeacherCreate(TeacherBase):
    initial_password: str

class TeacherUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    title: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None

class Teacher(TeacherBase):
    id: int
    is_active: bool
    last_login_at: Optional[datetime] = None
    created_by: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 