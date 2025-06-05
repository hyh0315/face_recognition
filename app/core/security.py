from datetime import datetime, timedelta, timezone
from typing import Optional, Tuple, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
import hashlib
from sqlalchemy import Column
from .config import settings
from app.schemas.auth import TokenData, UserType

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: Union[str, Column[str]]) -> bool:
    return pwd_context.verify(plain_password, str(hashed_password))

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[TokenData]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: Optional[str] = payload.get("sub")
        user_type: Optional[str] = payload.get("user_type")
        username: Optional[str] = payload.get("username")
        need_change_password: bool = payload.get("need_change_password", False)
        if user_id is None or user_type is None or username is None:
            return None
        return TokenData(
            user_id=int(user_id),
            user_type=UserType(user_type),
            username=username,
            need_change_password=need_change_password
        )
    except JWTError:
        return None



def verify_password_with_salt(password: str, salt: str, timestamp: int) -> str:
    """验证前端加密的密码"""
    data = f"{password}{timestamp}{salt}"
    return hashlib.sha256(data.encode()).hexdigest() 