from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.db.base import get_db
from app.schemas.auth import UserType, TokenData, UserResponse, AdminCreate
from app.db.models.admin import Admin
from app.api.deps import get_current_user

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