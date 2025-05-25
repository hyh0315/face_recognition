from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class StudentBase(BaseModel):
    username: str
    email: EmailStr
    student_id: str
    name: str
    class_name: Optional[str] = None

class StudentCreate(StudentBase):
    password: str

class Student(StudentBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True 