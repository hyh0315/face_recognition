from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

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
    is_active = Column(Boolean, default=False)  # 账号状态，默认未激活
    initial_password = Column(String)  # 初始密码
    created_by = Column(Integer, ForeignKey("admins.id"))  # 创建者
    
    # 统计字段
    total_attendance_count = Column(Integer, default=0)  # 总出勤次数
    total_late_count = Column(Integer, default=0)       # 总迟到次数
    total_absence_count = Column(Integer, default=0)    # 总缺勤次数
    total_leave_count = Column(Integer, default=0)      # 总请假次数
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # 关系
    attendances = relationship("Attendance", back_populates="student")
    absences = relationship("Absence", back_populates="student")

    # 添加新字段
    department = Column(String)  # 院系
    major = Column(String)      # 专业
    grade = Column(String)      # 年级
    is_graduated = Column(Boolean, default=False)  # 是否已毕业
    last_login_at = Column(DateTime(timezone=True), nullable=True)  # 最后登录时间
    