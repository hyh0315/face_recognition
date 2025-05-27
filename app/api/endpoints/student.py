from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime
from typing import List, Optional

from app.db.base import get_db
from app.api.deps import get_current_user
from app.schemas.auth import TokenData, UserType
from app.schemas.attendance import AttendanceRecord, AttendanceFilter, AttendanceListResponse
from app.db.models.attendance import Attendance
from app.db.models.attendance_task import AttendanceTask
from app.db.models.teacher import Teacher

router = APIRouter()

@router.get(
    "/attendance-records",
    response_model=AttendanceListResponse,
    summary="获取学生签到记录",
    description="""
    获取学生的签到记录，支持多种筛选条件：
    - 日期范围
    - 教师
    - 签到状态
    - 签到任务
    """,
    responses={
        200: {
            "description": "成功获取签到记录",
            "content": {
                "application/json": {
                    "example": {
                        "total": 10,
                        "items": [
                            {
                                "id": 1,
                                "task_id": 1,
                                "task_title": "早课签到",
                                "teacher_name": "张老师",
                                "status": "normal",
                                "late_minutes": 0,
                                "remark": None,
                                "created_at": "2024-03-20T08:00:00"
                            }
                        ]
                    }
                }
            }
        },
        401: {"description": "未授权访问"}
    }
)
async def get_attendance_records(
    filter_params: AttendanceFilter = Depends(),
    current_user: TokenData = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取学生签到记录
    
    参数:
        filter_params: 筛选条件
            - start_date: 开始日期
            - end_date: 结束日期
            - teacher_id: 教师ID
            - status: 签到状态
            - task_id: 签到任务ID
        current_user: 当前登录用户信息
        db: 数据库会话
    
    返回:
        AttendanceListResponse: 包含签到记录列表的响应
    """
    if current_user.user_type != UserType.STUDENT:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )

    # 构建查询
    query = db.query(
        Attendance,
        AttendanceTask.title.label("task_title"),
        Teacher.name.label("teacher_name")
    ).join(
        AttendanceTask,
        Attendance.task_id == AttendanceTask.id
    ).join(
        Teacher,
        AttendanceTask.teacher_id == Teacher.id
    ).filter(
        Attendance.student_id == current_user.user_id
    )

    # 应用筛选条件
    if filter_params.start_date:
        query = query.filter(Attendance.check_in_time >= filter_params.start_date)
    if filter_params.end_date:
        query = query.filter(Attendance.check_in_time <= filter_params.end_date)
    if filter_params.teacher_id:
        query = query.filter(AttendanceTask.teacher_id == filter_params.teacher_id)
    if filter_params.status:
        query = query.filter(Attendance.status == filter_params.status)
    if filter_params.task_id:
        query = query.filter(Attendance.task_id == filter_params.task_id)

    # 按签到时间倒序排序
    query = query.order_by(Attendance.check_in_time.desc())

    # 执行查询
    results = query.all()

    # 转换为响应模型
    items = []
    for attendance, task_title, teacher_name in results:
        items.append(
            AttendanceRecord(
                id=attendance.id,
                task_id=attendance.task_id,
                task_title=task_title,
                teacher_name=teacher_name,
                status=attendance.status,
                late_minutes=attendance.late_minutes,
                remark=attendance.remark,
                created_at=attendance.check_in_time
            )
        )

    return AttendanceListResponse(
        total=len(items),
        items=items
    ) 