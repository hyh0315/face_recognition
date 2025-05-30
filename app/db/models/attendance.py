from sqlalchemy import Column, Integer, DateTime, ForeignKey, String, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..base import Base

class AttendanceStatus(str, enum.Enum):
    NORMAL = "normal"      # 正常签到
    LATE = "late"         # 迟到
    LEAVE = "leave"       # 请假
    ABSENT = "absent"     # 缺勤

class Attendance(Base):
    __tablename__ = "attendance"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"))
    task_id = Column(Integer, ForeignKey("attendance_tasks.id"))
    check_in_time = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(AttendanceStatus), default=AttendanceStatus.NORMAL)
    late_minutes = Column(Integer, default=0)  # 迟到分钟数
    remark = Column(String, nullable=True)  # 备注

    # 关系
    student = relationship("Student", back_populates="attendances")
    task = relationship("AttendanceTask", back_populates="attendances") 