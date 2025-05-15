from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..base import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    student_id = Column(String, unique=True, index=True)  # 学号
    name = Column(String)  # 学生姓名
    class_name = Column(String)  # 班级
    face_encoding = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    attendances = relationship("Attendance", back_populates="student")
    absences = relationship("Absence", back_populates="student") 