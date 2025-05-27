from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.core.security import get_password_hash
from app.db.base import get_db
from app.schemas.auth import (
    UserType, TokenData, UserResponse,
    AdminCreate, TeacherCreate, StudentCreate,
    StudentFilter, StudentListResponse
)
from app.db.models.admin import Admin
from app.db.models.teacher import Teacher
from app.db.models.student import Student
from app.api.deps import get_current_user
from app.core.face_recognition import process_face_image, save_face_encoding
import secrets
import base64
import os
from pathlib import Path
import pandas as pd
from io import BytesIO
from typing import List

router = APIRouter()

@router.post(
    "/admin",
    response_model=UserResponse,
    summary="创建管理员账号",
    description="""
    创建新的管理员账号。
    - 需要超级管理员权限
    - 可以设置是否为超级管理员
    """,
    responses={
        201: {"description": "成功创建管理员账号"},
        403: {"description": "权限不足"},
        400: {"description": "参数错误"}
    }
)
async def create_admin(
    admin_data: AdminCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建管理员账号
    
    参数:
        admin_data: 管理员信息
        current_user: 当前登录用户信息
        db: 数据库会话
    
    返回:
        UserResponse: 创建的管理员信息
    """
    # 检查当前用户是否为超级管理员
    current_admin = db.query(Admin).filter(Admin.id == current_user.user_id).first()
    if current_admin is None or current_admin.is_super_admin is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can create admin accounts"
        )

    # 检查用户名和邮箱是否已存在
    if db.query(Admin).filter(Admin.username == admin_data.username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    if db.query(Admin).filter(Admin.email == admin_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # 创建管理员账号
    db_admin = Admin(
        username=admin_data.username,
        email=admin_data.email,
        hashed_password=get_password_hash(admin_data.password),
        name=admin_data.name,
        is_super_admin=admin_data.is_super_admin,
        phone=admin_data.phone
    )

    db.add(db_admin)
    db.commit()
    db.refresh(db_admin)

    return db_admin

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
    "/student",
    response_model=UserResponse,
    summary="创建学生账号",
    description="""
    创建新的学生账号。
    - 需要管理员权限
    - 自动生成初始密码
    - 账号默认未激活，需要学生首次登录修改密码
    - 需要上传学生人脸图片
    """,
    responses={
        201: {"description": "成功创建学生账号"},
        403: {"description": "权限不足"},
        400: {"description": "参数错误或人脸识别失败"}
    }
)
async def create_student(
    student_data: StudentCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建学生账号
    
    参数:
        student_data: 学生信息
        current_user: 当前登录用户信息
        db: 数据库会话
    
    返回:
        UserResponse: 创建的学生信息
    """
    # 检查当前用户是否为管理员
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can create student accounts"
        )

    # 检查学号和邮箱是否已存在
    if db.query(Student).filter(Student.student_id == student_data.student_id).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student ID already registered"
        )
    if db.query(Student).filter(Student.email == student_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    try:
        # 处理人脸图片
        face_image_data = base64.b64decode(student_data.face_image)
        face_encoding = process_face_image(face_image_data)
        
        # 生成初始密码
        initial_password = secrets.token_urlsafe(8)
        hashed_password = get_password_hash(initial_password)

        # 创建学生账号
        db_student = Student(
            student_id=student_data.student_id,
            username=student_data.student_id,  # 使用学号作为用户名
            email=student_data.email,
            hashed_password=hashed_password,
            initial_password=hashed_password,  # 保存初始密码的哈希值
            name=student_data.name,
            class_name=student_data.class_name,
            department=student_data.department,
            major=student_data.major,
            grade=student_data.grade,
            created_by=current_user.user_id
        )

        db.add(db_student)
        db.commit()
        db.refresh(db_student)

        # 保存人脸编码
        student_id = str(db_student.student_id)
        save_face_encoding(student_id, face_encoding)

        # 返回学生信息（不包含密码）
        return db_student

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process face image: {str(e)}"
        )

@router.get(
    "/students",
    response_model=StudentListResponse,
    summary="查询学生列表",
    description="""
    查询学生列表，支持多种筛选条件：
    - 班级
    - 院系
    - 专业
    - 年级
    - 账号状态
    - 是否毕业
    """,
    responses={
        200: {"description": "成功获取学生列表"},
        403: {"description": "权限不足"}
    }
)
async def get_students(
    filter_params: StudentFilter = Depends(),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    查询学生列表
    
    参数:
        filter_params: 筛选条件
        current_user: 当前登录用户信息
        db: 数据库会话
    
    返回:
        StudentListResponse: 包含学生列表的响应
    """
    # 检查权限
    if current_user.user_type not in [UserType.ADMIN, UserType.TEACHER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin and teacher can view student list"
        )

    # 构建查询
    query = db.query(Student)

    # 应用筛选条件
    filters = []
    if filter_params.class_name:
        filters.append(Student.class_name == filter_params.class_name)
    if filter_params.department:
        filters.append(Student.department == filter_params.department)
    if filter_params.major:
        filters.append(Student.major == filter_params.major)
    if filter_params.grade:
        filters.append(Student.grade == filter_params.grade)
    if filter_params.is_active is not None:
        filters.append(Student.is_active == filter_params.is_active)
    if filter_params.is_graduated is not None:
        filters.append(Student.is_graduated == filter_params.is_graduated)

    # 应用所有筛选条件
    if filters:
        query = query.filter(and_(*filters))

    # 按学号排序
    query = query.order_by(Student.student_id)

    # 执行查询
    students = query.all()

    return StudentListResponse(
        total=len(students),
        items=students
    )

@router.post(
    "/students/batch",
    response_model=List[UserResponse],
    summary="批量导入学生",
    description="""
    通过Excel文件批量导入学生账号。
    - 需要管理员权限
    - Excel文件必须包含以下列：学号、姓名、邮箱、班级、院系、专业、年级
    - 每个学生的人脸图片需要单独上传
    """,
    responses={
        201: {"description": "成功导入学生账号"},
        403: {"description": "权限不足"},
        400: {"description": "文件格式错误或数据验证失败"}
    }
)
async def batch_create_students(
    file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量导入学生账号
    
    参数:
        file: Excel文件
        current_user: 当前登录用户信息
        db: 数据库会话
    
    返回:
        List[UserResponse]: 创建的学生信息列表
    """
    # 检查当前用户是否为管理员
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can batch create student accounts"
        )

    # 检查文件类型
    if not file.filename or not file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )

    try:
        # 读取Excel文件
        contents = await file.read()
        df = pd.read_excel(BytesIO(contents))

        # 验证必要的列是否存在
        required_columns = ['学号', '姓名', '邮箱', '班级', '院系', '专业', '年级']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )

        # 创建学生账号
        created_students = []
        for _, row in df.iterrows():
            # 检查学号和邮箱是否已存在
            if db.query(Student).filter(Student.student_id == row['学号']).first():
                continue
            if db.query(Student).filter(Student.email == row['邮箱']).first():
                continue

            # 生成初始密码
            initial_password = secrets.token_urlsafe(8)
            hashed_password = get_password_hash(initial_password)

            # 创建学生账号
            db_student = Student(
                student_id=row['学号'],
                username=row['学号'],
                email=row['邮箱'],
                hashed_password=hashed_password,
                initial_password=hashed_password,
                name=row['姓名'],
                class_name=row['班级'],
                department=row['院系'],
                major=row['专业'],
                grade=row['年级'],
                created_by=current_user.user_id
            )

            db.add(db_student)
            db.commit()
            db.refresh(db_student)
            created_students.append(db_student)

        return created_students

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process Excel file: {str(e)}"
        ) 