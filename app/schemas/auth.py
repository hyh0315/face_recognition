from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from enum import Enum

class UserType(str, Enum):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_type: UserType
    user_id: int
    username: str
    need_change_password: bool = False

class TokenData(BaseModel):
    user_id: int
    user_type: UserType
    username: str
    need_change_password: bool = False

class LoginRequest(BaseModel):
    username: str
    password: str  # 前端加密后的密码

class ChangePasswordRequest(BaseModel):
    old_password: str  # 前端加密后的旧密码
    new_password: str  # 前端加密后的新密码 