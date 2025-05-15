from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class AttendanceTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime

class AttendanceTaskCreate(AttendanceTaskBase):
    student_ids: List[int]

class AttendanceTask(AttendanceTaskBase):
    id: int
    teacher_id: int
    created_at: datetime

    class Config:
        from_attributes = True 