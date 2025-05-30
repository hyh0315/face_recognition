from fastapi import APIRouter
from app.api.endpoints import admin_management, teacher_management, student_management

api_router = APIRouter()

# 管理员相关路由
api_router.include_router(
    admin_management.router,
    prefix="/admin",
    tags=["管理员管理"]
)

# 教师相关路由
api_router.include_router(
    teacher_management.router,
    prefix="/teacher",
    tags=["教师管理"]
)

# 学生相关路由
api_router.include_router(
    student_management.router,
    prefix="/student",
    tags=["学生管理"]
) 