from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
from .student import Student
from app.db.models.attendance_task import TaskStatus

class AttendanceTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    late_threshold: int = 15
    is_face_required: bool = True

class AttendanceTaskCreate(AttendanceTaskBase):
    student_ids: Optional[List[int]] = None  # 可选的学生ID列表
    class_names: Optional[List[str]] = None  # 可选的班级列表

class AttendanceTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    late_threshold: Optional[int] = None
    is_face_required: Optional[bool] = None
    status: Optional[TaskStatus] = None

class AttendanceTask(AttendanceTaskBase):
    id: int
    teacher_id: int
    status: TaskStatus
    created_at: datetime
    updated_at: Optional[datetime] = None
    students: List[Student]

    class Config:
        from_attributes = True 