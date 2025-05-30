from deepface import DeepFace
import numpy as np
import os
from pathlib import Path
from PIL import Image
import io

FACE_ENCODINGS_DIR = Path("data/face_encodings")

def process_face_image(image_data: bytes) -> np.ndarray:
    """处理人脸图片并提取特征"""
    # 将字节数据转换为PIL图像
    image = Image.open(io.BytesIO(image_data))
    # 使用DeepFace提取人脸特征
    embedding = DeepFace.represent(
        img_path=np.array(image),
        model_name="Facenet",
        enforce_detection=True
    )
    return np.array(embedding[0]["embedding"])

def save_face_encoding(user_id: str, face_encoding: np.ndarray):
    """保存人脸特征编码"""
    # 确保目录存在
    FACE_ENCODINGS_DIR.mkdir(parents=True, exist_ok=True)
    # 保存特征编码
    np.save(FACE_ENCODINGS_DIR / f"{user_id}.npy", face_encoding)

def delete_face_encoding(user_id: str):
    """删除人脸特征编码文件"""
    encoding_file = FACE_ENCODINGS_DIR / f"{user_id}.npy"
    if encoding_file.exists():
        encoding_file.unlink() 