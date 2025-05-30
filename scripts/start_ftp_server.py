import os
import sys
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = str(Path(__file__).parent.parent)
sys.path.append(project_root)

from app.core.ftp_server import ftp_service
from app.core.config import settings

async def main():
    """启动FTP服务器"""
    try:
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # 启动FTP服务器
        await ftp_service.start(
            host=settings.FTP_SERVER_HOST,
            port=settings.FTP_SERVER_PORT
        )
        
    except KeyboardInterrupt:
        logging.info("正在关闭FTP服务器...")
        await ftp_service.stop()
        logging.info("FTP服务器已关闭")
    except Exception as e:
        logging.error(f"FTP服务器运行出错: {str(e)}")
        await ftp_service.stop()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 