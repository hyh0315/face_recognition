from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func
from app.db.base_class import Base

class Admin(Base):
    __tablename__ = "admins"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String)  # 管理员姓名
    is_super_admin = Column(Boolean, default=False)  # 超级管理员标志
    phone = Column(String, nullable=True)      # 联系电话，可选
    last_login_at = Column(DateTime(timezone=True), nullable=True)  # 最后登录时间
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Admin(id={self.id}, username={self.username}, email={self.email})>" 