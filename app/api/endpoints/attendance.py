from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from app.db.base import get_db
from app.api.deps import get_current_user
from app.schemas.auth import TokenData, UserType
from app.schemas.attendance_task import AttendanceTaskCreate, AttendanceTask
from app.db.models.attendance_task import AttendanceTask as AttendanceTaskModel
from app.db.models.teacher import Teacher
from app.db.models.student import Student

router = APIRouter()

@router.get("/")
async def get_attendance():
    return {"message": "考勤功能待实现"}

@router.post(
    "/tasks",
    response_model=AttendanceTask,
    summary="发布签到任务",
    description="""
    教师发布新的签到任务，可以指定：
    - 任务标题和描述
    - 开始和结束时间
    - 迟到阈值
    - 是否需要人脸识别
    - 参与学生（可通过学生ID列表或班级列表选择）
    """,
    responses={
        201: {"description": "成功创建签到任务"},
        403: {"description": "权限不足"},
        404: {"description": "学生不存在"},
        400: {"description": "参数错误"}
    }
)
async def create_attendance_task(
    task: AttendanceTaskCreate,
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    创建新的签到任务
    
    参数:
        task: 签到任务信息
            - student_ids: 可选的学生ID列表
            - class_names: 可选的班级列表
        current_user: 当前登录用户信息
        db: 数据库会话
    
    返回:
        AttendanceTask: 创建的签到任务信息
    """
    if current_user.user_type != UserType.TEACHER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can create attendance tasks"
        )

    # 验证时间
    if task.start_time >= task.end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="End time must be after start time"
        )

    # 获取参与学生
    students = []
    if task.student_ids:
        # 通过学生ID选择
        students = db.query(Student).filter(Student.id.in_(task.student_ids)).all()
        if len(students) != len(task.student_ids):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Some students not found"
            )
    elif task.class_names:
        # 通过班级选择
        students = db.query(Student).filter(Student.class_name.in_(task.class_names)).all()
        if not students:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No students found in the specified classes"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either student_ids or class_names must be provided"
        )

    # 创建签到任务
    db_task = AttendanceTaskModel(
        title=task.title,
        description=task.description,
        start_time=task.start_time,
        end_time=task.end_time,
        late_threshold=task.late_threshold,
        is_face_required=task.is_face_required,
        teacher_id=current_user.user_id,
        students=students
    )

    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    return db_task 