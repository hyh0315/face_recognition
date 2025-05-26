from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.db.base_class import Base

# 创建数据库引擎
engine = create_engine(
    settings.DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 导入所有模型，确保它们被注册到 Base.metadata
from app.db.models.attendance_task import AttendanceTask  # 先导入
from app.db.models.admin import Admin
from app.db.models.teacher import Teacher
from app.db.models.student import Student
from app.db.models.attendance import Attendance
from app.db.models.absence import Absence

# 依赖项
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 