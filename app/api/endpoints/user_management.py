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
from app.core.face_recognition import process_face_image, save_face_encoding, delete_face_encoding
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
    - 需要同时上传一个zip文件，包含所有学生的人脸图片，图片命名格式为：学号.jpg
    """,
    responses={
        201: {"description": "成功导入学生账号"},
        403: {"description": "权限不足"},
        400: {"description": "文件格式错误或数据验证失败"}
    }
)
async def batch_create_students(
    excel_file: UploadFile = File(...),
    face_images: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量导入学生账号
    
    参数:
        excel_file: Excel文件
        face_images: 包含人脸图片的zip文件
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

    # 检查Excel文件类型
    if not excel_file.filename or not excel_file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )

    # 检查zip文件类型
    if not face_images.filename or not face_images.filename.endswith('.zip'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Face images must be uploaded as a zip file"
        )

    try:
        # 读取Excel文件
        contents = await excel_file.read()
        df = pd.read_excel(BytesIO(contents))

        # 验证必要的列是否存在
        required_columns = ['学号', '姓名', '邮箱', '班级', '院系', '专业', '年级']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )

        # 读取并解压人脸图片zip文件
        import zipfile
        import tempfile
        import os

        face_images_content = await face_images.read()
        with tempfile.TemporaryDirectory() as temp_dir:
            zip_path = os.path.join(temp_dir, "face_images.zip")
            with open(zip_path, "wb") as f:
                f.write(face_images_content)

            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(temp_dir)

            # 创建学生账号
            created_students = []
            for _, row in df.iterrows():
                student_id = str(row['学号'])
                face_image_path = os.path.join(temp_dir, f"{student_id}.jpg")

                # 检查学号和邮箱是否已存在
                if db.query(Student).filter(Student.student_id == student_id).first():
                    continue
                if db.query(Student).filter(Student.email == row['邮箱']).first():
                    continue

                # 检查人脸图片是否存在
                if not os.path.exists(face_image_path):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Face image not found for student {student_id}"
                    )

                try:
                    # 处理人脸图片
                    with open(face_image_path, 'rb') as f:
                        face_image_data = f.read()
                    face_encoding = process_face_image(face_image_data)

                    # 生成初始密码
                    initial_password = secrets.token_urlsafe(8)
                    hashed_password = get_password_hash(initial_password)

                    # 创建学生账号
                    db_student = Student(
                        student_id=student_id,
                        username=student_id,
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

                    # 保存人脸编码
                    save_face_encoding(student_id, face_encoding)
                    created_students.append(db_student)

                except Exception as e:
                    db.rollback()
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Failed to process face image for student {student_id}: {str(e)}"
                    )

        return created_students

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process files: {str(e)}"
        )

@router.post(
    "/teachers/batch",
    response_model=List[UserResponse],
    summary="批量导入教师",
    description="""
    通过Excel文件批量导入教师账号。
    - 需要管理员权限
    - Excel文件必须包含以下列：教师编号、姓名、邮箱、职称、院系、手机号
    - 自动生成初始密码
    - 账号默认未激活，需要教师首次登录修改密码
    """,
    responses={
        201: {"description": "成功导入教师账号"},
        403: {"description": "权限不足"},
        400: {"description": "文件格式错误或数据验证失败"}
    }
)
async def batch_create_teachers(
    excel_file: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量导入教师账号
    
    参数:
        excel_file: Excel文件
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

    # 检查Excel文件类型
    if not excel_file.filename or not excel_file.filename.endswith(('.xlsx', '.xls')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only Excel files (.xlsx, .xls) are allowed"
        )

    try:
        # 读取Excel文件
        contents = await excel_file.read()
        df = pd.read_excel(BytesIO(contents))

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
    "/student/{student_id}",
    summary="删除学生账号",
    description="""
    删除指定学号的学生账号。
    - 需要管理员权限
    - 会同时删除学生的人脸编码数据
    - 会同时删除学生的考勤记录
    """,
    responses={
        200: {"description": "成功删除学生账号"},
        403: {"description": "权限不足"},
        404: {"description": "学生不存在"}
    }
)
async def delete_student(
    student_id: str,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除学生账号
    
    参数:
        student_id: 学生学号
        current_user: 当前登录用户信息
        db: 数据库会话
    
    返回:
        dict: 删除结果
    """
    # 检查当前用户是否为管理员
    if current_user.user_type != UserType.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin can delete student accounts"
        )

    # 查找学生
    student = db.query(Student).filter(Student.student_id == student_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with ID {student_id} not found"
        )

    try:
        # 删除学生的人脸编码数据
        delete_face_encoding(student_id)

        # 删除学生账号
        db.delete(student)
        db.commit()

        return {
            "message": f"Successfully deleted student {student_id}",
            "student_id": student_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete student: {str(e)}"
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

@router.delete(
    "/admin/{admin_id}",
    summary="删除管理员账号",
    description="""
    删除指定ID的管理员账号。
    - 需要超级管理员权限
    - 不能删除自己
    - 不能删除最后一个超级管理员
    - 会同时删除该管理员创建的所有账号记录
    """,
    responses={
        200: {"description": "成功删除管理员账号"},
        403: {"description": "权限不足或不能删除自己/最后一个超级管理员"},
        404: {"description": "管理员不存在"}
    }
)
async def delete_admin(
    admin_id: int,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除管理员账号
    
    参数:
        admin_id: 管理员ID
        current_user: 当前登录用户信息
        db: 数据库会话
    
    返回:
        dict: 删除结果
    """
    # 检查当前用户是否为超级管理员
    current_admin = db.query(Admin).filter(Admin.id == current_user.user_id).first()
    if current_admin is None or current_admin.is_super_admin is False:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only super admin can delete admin accounts"
        )

    # 不能删除自己
    if admin_id == current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete your own account"
        )

    # 查找要删除的管理员
    admin_to_delete = db.query(Admin).filter(Admin.id == admin_id).first()
    if not admin_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Admin with ID {admin_id} not found"
        )

    # 如果要删除的是超级管理员，检查是否是最后一个超级管理员
    if admin_to_delete.is_super_admin is True:
        super_admin_count = db.query(Admin).filter(Admin.is_super_admin.is_(True)).count()
        if super_admin_count <= 1:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete the last super admin"
            )

    try:
        # 删除管理员账号（由于设置了级联删除，相关的创建记录也会被自动删除）
        db.delete(admin_to_delete)
        db.commit()

        return {
            "message": f"Successfully deleted admin {admin_id}",
            "admin_id": admin_id
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete admin: {str(e)}"
        ) 