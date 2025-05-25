from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..base import Base

# 多对多关系表：任务与学生
task_students = Table(
    'task_students',
    Base.metadata,
    Column('task_id', Integer, ForeignKey('attendance_tasks.id')),
    Column('student_id', Integer, ForeignKey('students.id'))
)

class AttendanceTask(Base):
    __tablename__ = "attendance_tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String)
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 外键
    teacher_id = Column(Integer, ForeignKey("teachers.id"))

    # 关系
    teacher = relationship("Teacher", back_populates="created_tasks")
    students = relationship("Student", secondary=task_students)
    attendances = relationship("Attendance", back_populates="task")
    absences = relationship("Absence", back_populates="task")  # 添加缺勤关系 