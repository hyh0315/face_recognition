from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.db.base_class import Base
from app.db.base import engine
from app.db.models.admin import Admin
from app.db.models.teacher import Teacher
from app.db.models.student import Student

def init_db() -> None:
    """初始化数据库"""
    # 创建所有表
    Base.metadata.create_all(bind=engine)

def create_initial_admin(db: Session) -> None:
    """创建初始管理员账号"""
    # 检查是否已存在管理员
    admin = db.query(Admin).first()
    if not admin:
        # 创建初始管理员账号
        admin = Admin(
            username="admin",
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            name="系统管理员",
            is_super_admin=True  # 设置为超级管理员
        )
        db.add(admin)
        db.commit()
        print("初始管理员账号创建成功")

def create_test_accounts(db: Session) -> None:


    # 创建测试教师账号
    teacher = Teacher(
        username="teacher1",
        email="teacher1@example.com",
        hashed_password=get_password_hash("teacher123"),
        initial_password=get_password_hash("teacher123"),
        name="测试教师",
        title="讲师",
        department="计算机系",
        phone="13800138000",
        is_active=False,
        teacher_id="T2024001"  # 添加教师编号
    )
    db.add(teacher)

    # 创建测试学生账号
    student = Student(
        username="student1",
        email="student1@example.com",
        hashed_password=get_password_hash("student123"),
        initial_password=get_password_hash("student123"),
        name="测试学生",
        student_id="2024001",
        class_name="计算机1班",
        is_active=False
    )
    db.add(student)

    db.commit()
    print("测试账号创建成功")

if __name__ == "__main__":
    from app.db.base import SessionLocal
    
    # 初始化数据库
    init_db()
    
    # 创建数据库会话
    db = SessionLocal()
    try:
        # 创建初始管理员账号
        create_initial_admin(db)
        
        # 创建测试账号
        create_test_accounts(db)
    finally:
        db.close() 