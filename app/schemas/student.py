from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class StudentBase(BaseModel):
    username: str
    email: EmailStr
    student_id: str
    name: str
    class_name: str
    department: str
    major: str
    grade: str

class StudentCreate(StudentBase):
    initial_password: str

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    class_name: Optional[str] = None
    department: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None
    is_active: Optional[bool] = None
    is_graduated: Optional[bool] = None

class Student(StudentBase):
    id: int
    is_active: bool
    is_graduated: bool
    last_login_at: Optional[datetime] = None
    created_by: int
    total_attendance_count: int
    total_late_count: int
    total_absence_count: int
    total_leave_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 