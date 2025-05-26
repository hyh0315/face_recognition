from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.security import (
    verify_password, create_access_token, get_password_hash,
    verify_password_with_salt
)
from app.core.config import settings
from app.db.base import get_db
from app.schemas.auth import Token, UserType, ChangePasswordRequest, TokenData
from app.db.models.admin import Admin
from app.db.models.teacher import Teacher
from app.db.models.student import Student
from app.api.deps import get_current_user

router = APIRouter()

@router.post(
    "/login",
    response_model=Token,
    summary="用户登录",
    description="""
    用户登录接口，支持管理员、教师和学生三种角色登录。
    - 验证用户名和密码
    - 检查账号状态
    - 返回JWT访问令牌
    - 首次登录需要修改密码
    """,
    responses={
        200: {
            "description": "登录成功",
            "content": {
                "application/json": {
                    "example": {
                        "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "token_type": "bearer",
                        "user_type": "teacher",
                        "user_id": 1,
                        "username": "teacher1",
                        "need_change_password": False
                    }
                }
            }
        },
        401: {"description": "用户名或密码错误"}
    }
)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    
    参数:
        form_data: OAuth2密码流程的表单数据
            - username: 用户名
            - password: 密码
        db: 数据库会话
    
    返回:
        Token: 包含访问令牌和用户信息的响应
    """
    # 尝试所有用户类型
    user = None
    user_type = None
    
    # 检查管理员
    admin = db.query(Admin).filter(Admin.username == form_data.username).first()
    if admin and verify_password(form_data.password, admin.hashed_password):
        user = admin
        user_type = UserType.ADMIN
    
    # 检查教师
    if not user:
        teacher = db.query(Teacher).filter(Teacher.username == form_data.username).first()
        if teacher and verify_password(form_data.password, teacher.hashed_password):
            user = teacher
            user_type = UserType.TEACHER
    
    # 检查学生
    if not user:
        student = db.query(Student).filter(Student.student_id == form_data.username).first()
        if student and verify_password(form_data.password, student.hashed_password):
            user = student
            user_type = UserType.STUDENT

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 检查是否是初始密码
    need_change_password = False
    if hasattr(user, 'initial_password'):
        if verify_password(form_data.password, user.initial_password):
            need_change_password = True

    # 创建访问令牌
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": str(user.id),  # 确保id是字符串
            "user_type": user_type,
            "username": user.username,
            "need_change_password": need_change_password
        },
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_type": user_type,
        "user_id": user.id,
        "username": user.username,
        "need_change_password": need_change_password
    }

@router.post(
    "/change-password",
    summary="修改密码",
    description="""
    修改用户密码接口。
    
    - 需要提供旧密码进行验证
    - 新密码需要符合密码复杂度要求
    - 首次登录修改密码后会激活账号
    """,
    responses={
        200: {
            "description": "密码修改成功",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Password changed successfully"
                    }
                }
            }
        },
        400: {"description": "旧密码错误"},
        401: {"description": "未授权访问"},
        404: {"description": "用户不存在"}
    }
)
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    修改密码接口
    
    参数:
        password_data: 密码修改请求数据
            - old_password: 旧密码
            - new_password: 新密码
        current_user: 当前登录用户信息
        db: 数据库会话
    
    返回:
        dict: 包含成功消息的响应
    """
    # 根据用户类型选择对应的模型
    if current_user.user_type == UserType.ADMIN:
        user = db.query(Admin).filter(Admin.id == current_user.user_id).first()
    elif current_user.user_type == UserType.TEACHER:
        user = db.query(Teacher).filter(Teacher.id == current_user.user_id).first()
    else:
        user = db.query(Student).filter(Student.id == current_user.user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # 验证旧密码
    if not verify_password(password_data.old_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect old password"
        )

    # 更新密码
    setattr(user, 'hashed_password', get_password_hash(password_data.new_password))
    if hasattr(user, 'is_active'):
        setattr(user, 'is_active', True)  # 激活账号
    
    db.commit()

    return {"message": "Password changed successfully"} 