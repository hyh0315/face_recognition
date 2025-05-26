from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.db.models.absence import AbsenceStatus

class AbsenceBase(BaseModel):
    student_id: int
    task_id: int
    reason: str

class AbsenceCreate(AbsenceBase):
    pass

class AbsenceUpdate(BaseModel):
    status: AbsenceStatus
    remark: Optional[str] = None

class Absence(AbsenceBase):
    id: int
    status: AbsenceStatus
    approved_by: Optional[int] = None
    approved_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True 