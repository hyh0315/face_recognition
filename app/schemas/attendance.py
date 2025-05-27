from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional
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

class AttendanceRecord(BaseModel):
    id: int
    task_id: int
    task_title: str
    teacher_name: str
    status: AttendanceStatus
    late_minutes: int
    remark: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AttendanceFilter(BaseModel):
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    teacher_id: Optional[int] = None
    status: Optional[AttendanceStatus] = None
    task_id: Optional[int] = None

class AttendanceListResponse(BaseModel):
    total: int
    items: List[AttendanceRecord] 