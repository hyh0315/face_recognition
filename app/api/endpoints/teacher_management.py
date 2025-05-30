from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.db.base import get_db
from app.schemas.auth import UserType, TokenData, UserResponse, TeacherCreate
from app.db.models.teacher import Teacher
from app.api.deps import get_current_user
from app.core.ftp_server import ftp_service
from app.core.config import settings
import secrets
import pandas as pd
from io import BytesIO
from typing import List
import ftplib
from datetime import datetime
import tempfile
import os

router = APIRouter()

@router.post(
    "/teacher",
    response_model=UserResponse,
    summary="创建教师账号",
    description="""
    创建新的教师账号。
    - 需要管理员权限
    - 自动生成初始密码
    - 账号默认未激活，需要教师首次登录修改密码
    """,
    responses={
        201: {"description": "成功创建教师账号"},
        403: {"description": "权限不足"},
        400: {"description": "参数错误"}
    }
)
async def create_teacher(
    teacher_data: TeacherCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建教师账号
    
    参数:
        teacher_data: 教师信息
        current_user: 当前登录用户信息
        db: 数据库会话
    
    返回:
        UserResponse: 创建的教师信息
    """
    # 检查当前用户是否为管理员
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can create teacher accounts"
        )

    # 检查教师编号和邮箱是否已存在
    if db.query(Teacher).filter(Teacher.teacher_id == teacher_data.teacher_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Teacher ID already registered"
        )
    if db.query(Teacher).filter(Teacher.email == teacher_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 生成初始密码
    initial_password = secrets.token_urlsafe(8)
    hashed_password = get_password_hash(initial_password)

    # 创建教师账号
    db_teacher = Teacher(
        teacher_id=teacher_data.teacher_id,
        username=teacher_data.teacher_id,  # 使用教师编号作为用户名
        email=teacher_data.email,
        hashed_password=hashed_password,
        initial_password=hashed_password,  # 保存初始密码的哈希值
        name=teacher_data.name,
        title=teacher_data.title,
        department=teacher_data.department,
        phone=teacher_data.phone,
        created_by=current_user.user_id
    )

    db.add(db_teacher)
    db.commit()
    db.refresh(db_teacher)

    # 返回教师信息（不包含密码）
    return db_teacher

@router.post(
    "/teachers/batch",
    response_model=List[UserResponse],
    summary="批量导入教师",
    description="""
    批量导入教师账号。
    - 需要管理员权限
    - 前端需要先将Excel文件上传到FTP服务器
    - Excel文件必须包含以下列：教师编号、姓名、邮箱、职称、院系、手机号
    - 自动生成初始密码
    - 账号默认未激活，需要教师首次登录修改密码
    """,
    responses={
        201: {"description": "成功导入教师账号"},
        403: {"description": "权限不足"},
        400: {"description": "数据验证失败"}
    }
)
async def batch_create_teachers(
    excel_path: str,  # FTP服务器上的Excel文件路径
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量导入教师账号
    
    参数:
        excel_path: FTP服务器上的Excel文件路径
        current_user: 当前登录用户信息
        db: 数据库会话
    
    返回:
        List[UserResponse]: 创建的教师信息列表
    """
    # 检查当前用户是否为管理员
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can batch create teacher accounts"
        )

    try:
        # 从FTP服务器下载Excel文件
        with tempfile.TemporaryDirectory() as temp_dir:
            excel_local_path = os.path.join(temp_dir, "teachers.xlsx")
            with ftplib.FTP() as ftp:
                ftp.connect(settings.FTP_SERVER_HOST, settings.FTP_SERVER_PORT)
                ftp.login()  # 匿名登录
                with open(excel_local_path, 'wb') as f:
                    ftp.retrbinary(f'RETR {excel_path}', f.write)

            # 读取Excel文件
            df = pd.read_excel(excel_local_path)

            # 验证必要的列是否存在
            required_columns = ['教师编号', '姓名', '邮箱', '职称', '院系', '手机号']
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Missing required columns: {', '.join(missing_columns)}"
                )

            # 创建教师账号
            created_teachers = []
            for _, row in df.iterrows():
                teacher_id = str(row['教师编号'])

                # 检查教师编号和邮箱是否已存在
                if db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first():
                    continue
                if db.query(Teacher).filter(Teacher.email == row['邮箱']).first():
                    continue

                try:
                    # 生成初始密码
                    initial_password = secrets.token_urlsafe(8)
                    hashed_password = get_password_hash(initial_password)

                    # 创建教师账号
                    db_teacher = Teacher(
                        teacher_id=teacher_id,
                        username=teacher_id,  # 使用教师编号作为用户名
                        email=row['邮箱'],
                        hashed_password=hashed_password,
                        initial_password=hashed_password,  # 保存初始密码的哈希值
                        name=row['姓名'],
                        title=row['职称'],
                        department=row['院系'],
                        phone=row['手机号'],
                        created_by=current_user.user_id
                    )

                    db.add(db_teacher)
                    db.commit()
                    db.refresh(db_teacher)
                    created_teachers.append(db_teacher)

                except Exception as e:
                    db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to create teacher account for {teacher_id}: {str(e)}"
                    )

        return created_teachers

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process Excel file: {str(e)}"
        )

@router.delete(
    "/teacher/{teacher_id}",
    summary="删除教师账号",
    description="""
    删除指定教师编号的教师账号。
    - 需要管理员权限
    - 会同时删除教师相关的课程记录
    - 会同时删除教师相关的考勤记录
    """,
    responses={
        200: {"description": "成功删除教师账号"},
        403: {"description": "权限不足"},
        404: {"description": "教师不存在"}
    }
)
async def delete_teacher(
    teacher_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除教师账号
    
    参数:
        teacher_id: 教师编号
        current_user: 当前登录用户信息
        db: 数据库会话
    
    返回:
        dict: 删除结果
    """
    # 检查当前用户是否为管理员
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete teacher accounts"
        )

    # 查找教师
    teacher = db.query(Teacher).filter(Teacher.teacher_id == teacher_id).first()
    if not teacher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Teacher with ID {teacher_id} not found"
        )

    try:
        # 删除教师账号（由于设置了级联删除，相关的课程和考勤记录也会被自动删除）
        db.delete(teacher)
        db.commit()

        return {
            "message": f"Successfully deleted teacher {teacher_id}",
            "teacher_id": teacher_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete teacher: {str(e)}"
        ) 