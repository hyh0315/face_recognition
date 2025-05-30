from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    teacher_id = Column(String, unique=True, index=True)  # 教师编号
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)  # 教师姓名
    title = Column(String)  # 职称
    is_active = Column(Boolean, default=False)  # 账号状态，默认未激活
    initial_password = Column(String)  # 初始密码
    created_by = Column(Integer, ForeignKey("admins.id"))  # 创建者
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    department = Column(String)  # 所属院系
    phone = Column(String)      # 联系电话
    last_login_at = Column(DateTime(timezone=True), nullable=True)  # 最后登录时间

    # 关系
    created_tasks = relationship("AttendanceTask", back_populates="teacher")
    approved_absences = relationship("Absence", back_populates="approver") 