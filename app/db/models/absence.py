from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..base import Base

class AbsenceStatus(str, enum.Enum):
    PENDING = "pending"    # 待审批
    APPROVED = "approved"  # 已批准
    REJECTED = "rejected"  # 已拒绝

class Absence(Base):
    __tablename__ = "absences"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    task_id = Column(Integer, ForeignKey("attendance_tasks.id"))
    reason = Column(String, nullable=False)  # 请假原因
    status = Column(Enum(AbsenceStatus), default=AbsenceStatus.PENDING)
    approved_by = Column(Integer, ForeignKey("teachers.id"), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # 关系
    student = relationship("Student", back_populates="absences")
    task = relationship("AttendanceTask", back_populates="absences")
    approver = relationship("Teacher") 