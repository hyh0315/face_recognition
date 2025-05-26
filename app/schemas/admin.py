from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional

class AdminBase(BaseModel):
    username: str
    email: EmailStr
    name: str
    phone: Optional[str] = None

class AdminCreate(AdminBase):
    password: str
    is_super_admin: bool = False

class AdminUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    password: Optional[str] = None

class Admin(AdminBase):
    id: int
    is_super_admin: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True 