from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Sequence
from enum import Enum
from datetime import datetime

class UserType(str):
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"

class Token(BaseModel):
    access_token: str
    token_type: str
    user_type: str
    user_id: int
    username: str
    need_change_password: bool

class TokenData(BaseModel):
    user_id: int
    user_type: str
    username: str
    need_change_password: bool

class LoginRequest(BaseModel):
    username: str
    password: str  # 前端加密后的密码

class ChangePasswordRequest(BaseModel):
    old_password: str
    new_password: str

# 新增的请求模型
class AdminCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: str = Field(..., min_length=2, max_length=50)
    is_super_admin: bool = False
    phone: Optional[str] = None

class TeacherCreate(BaseModel):
    teacher_id: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=50)
    title: str = Field(..., min_length=2, max_length=50)
    department: str = Field(..., min_length=2, max_length=100)
    phone: str = Field(..., min_length=11, max_length=11)

class TeacherUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    title: Optional[str] = Field(None, min_length=2, max_length=50)
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    phone: Optional[str] = Field(None, min_length=11, max_length=11)
    email: Optional[EmailStr] = None
    class Config:
        orm_mode = True

class StudentCreate(BaseModel):
    student_id: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    name: str = Field(..., min_length=2, max_length=50)
    class_name: str = Field(..., min_length=2, max_length=50)
    department: str = Field(..., min_length=2, max_length=100)
    major: str = Field(..., min_length=2, max_length=100)
    grade: str = Field(..., min_length=4, max_length=4)
    face_image: str = Field(..., description="Base64编码的人脸图片数据")

class StudentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    class_name: Optional[str] = Field(None, min_length=2, max_length=50)
    department: Optional[str] = Field(None, min_length=2, max_length=100)
    major: Optional[str] = Field(None, min_length=2, max_length=100)
    grade: Optional[str] = Field(None, min_length=4, max_length=4)
    email: Optional[EmailStr] = None

    class Config:
        orm_mode = True

class StudentResponse(BaseModel):
    id: int
    student_id: str
    name: str
    department: str
    major:str
    grade:str
    class_name:str
    email:EmailStr
    total_attendance_count:int
    total_late_count:int
    total_absence_count:int
    total_leave_count:int
    created_by: int

    class Config:
        orm_mode = True

class TeacherResponse(BaseModel):
    id: int
    teacher_id: str
    name: str
    title: str
    department: str
    phone: str
    email: EmailStr
    class Config:
        orm_mode=True

class StudentFilter(BaseModel):
    class_name: Optional[str] = None
    department: Optional[str] = None
    major: Optional[str] = None
    grade: Optional[str] = None

class StudentListResponse(BaseModel):
    total: int
    items: Sequence[StudentResponse]

    class Config:
        orm_mode = True

class TeacherFilter(BaseModel):
    title: Optional[str] = None
    department: Optional[str] = None

class TeacherListResponse(BaseModel):
    total: int
    items: Sequence[TeacherResponse]

    class Config:
        orm_mode = True 