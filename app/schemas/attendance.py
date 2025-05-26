from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.db.models.attendance import AttendanceStatus

class AttendanceBase(BaseModel):
    student_id: int
    task_id: int
    status: AttendanceStatus
    late_minutes: int = 0
    remark: Optional[str] = None

class AttendanceCreate(AttendanceBase):
    pass

class Attendance(AttendanceBase):
    id: int
    check_in_time: datetime
    created_at: datetime

    class Config:
        from_attributes = True 