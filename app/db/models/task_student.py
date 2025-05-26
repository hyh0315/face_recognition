from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean
from sqlalchemy.sql import func
from ..base import Base

class TaskStudent(Base):
    __tablename__ = "task_students"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("attendance_tasks.id"))
    student_id = Column(Integer, ForeignKey("students.id"))
    is_required = Column(Boolean, default=True)  # 是否必须参加
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 