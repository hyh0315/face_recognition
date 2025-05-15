from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..base import Base

class AbsenceType(str, enum.Enum):
    SICK = "sick"        # 病假
    PERSONAL = "personal"  # 事假
    UNKNOWN = "unknown"    # 未知原因

class Absence(Base):
    __tablename__ = "absences"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    task_id = Column(Integer, ForeignKey("attendance_tasks.id"))
    type = Column(Enum(AbsenceType), default=AbsenceType.UNKNOWN)
    reason = Column(String, nullable=True)
    proof_document = Column(String, nullable=True)  # 证明文件路径
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)  # 审批时间
    approved_by = Column(Integer, ForeignKey("teachers.id"), nullable=True)  # 审批教师

    # 关系
    student = relationship("Student", back_populates="absences")
    task = relationship("AttendanceTask", back_populates="absences")
    approver = relationship("Teacher") 