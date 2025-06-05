from pydantic_settings import BaseSettings
from typing import List, Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "人脸识别签到系统"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["*"]
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天

    class Config:
        case_sensitive = True
        env_file = ".env"

    # 数据库配置
    DATABASE_URL: str = "sqlite:///./face_recognition.db"

    # 文件服务器配置
    FILE_SERVER_BASE_DIR: str = "uploads"
    FILE_SERVER_URL_PREFIX: str = "/static"
    FILE_SERVER_MAX_FILE_SIZE: int = 2 * 1024 * 1024  # 2MB
    FILE_SERVER_ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png"]
    FILE_SERVER_ALLOWED_EXCEL_TYPES: list = ["application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"]

    # 人脸识别配置
    FACE_RECOGNITION_MODEL: str = "cnn"  # 或 "cnn"
    FACE_RECOGNITION_TOLERANCE: float = 0.6

settings = Settings() 