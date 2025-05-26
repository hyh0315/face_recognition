from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    PROJECT_NAME: str = "人脸识别签到系统"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days

    class Config:
        case_sensitive = True

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./face_recognition.db"

    # 人脸识别配置
    FACE_RECOGNITION_TOLERANCE: float = 0.6

settings = Settings() 