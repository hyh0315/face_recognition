import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.init_db import init_db, create_initial_admin, create_test_accounts
from app.db.base import SessionLocal

def main() -> None:
    print("开始初始化数据库...")
    
    # 初始化数据库
    init_db()
    
    # 创建数据库会话
    db = SessionLocal()
    try:
        # 创建初始管理员账号
        create_initial_admin(db)
        
        # 创建测试账号
        create_test_accounts(db)
        
        print("数据库初始化完成！")
    finally:
        db.close()

if __name__ == "__main__":
    main() 