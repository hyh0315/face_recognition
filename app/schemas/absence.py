from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.db.models.absence import AbsenceType

class AbsenceBase(BaseModel):
    student_id: int
    task_id: int
    type: AbsenceType
    reason: Optional[str] = None
    proof_document: Optional[str] = None

class AbsenceCreate(AbsenceBase):
    pass

class Absence(AbsenceBase):
    id: int
    created_at: datetime
    approved_at: Optional[datetime] = None
    approved_by: Optional[int] = None

    class Config:
        from_attributes = True 