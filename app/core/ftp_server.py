from pyftpdlib.authorizers import DummyAuthorizer
from pyftpdlib.handlers import FTPHandler, TLS_FTPHandler
from pyftpdlib.servers import FTPServer
from app.core.config import settings
import os
import logging
from typing import Optional
import ssl
import asyncio
from concurrent.futures import ThreadPoolExecutor

class CustomFTPHandler(TLS_FTPHandler):
    certfile = "server.cert"
    keyfile = "server.key"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.passive_dtp = True
        self.passive_ports = range(60000, 65535)
        # 启用CORS
        self.authorizer.add_anonymous(
            settings.FILE_SERVER_BASE_DIR,
            perm="elradfmw"  # 所有权限
        )
    
    def on_file_received(self, file):
        """文件上传完成时的回调"""
        logging.info(f"文件上传完成: {file}")
    
    def on_file_sent(self, file):
        """文件下载完成时的回调"""
        logging.info(f"文件下载完成: {file}")
    
    def on_incomplete_file_received(self, file):
        """文件上传失败时的回调"""
        logging.error(f"文件上传失败: {file}")
    
    def on_incomplete_file_sent(self, file):
        """文件下载失败时的回调"""
        logging.error(f"文件下载失败: {file}")

class FTPService:
    def __init__(self):
        self.authorizer = DummyAuthorizer()
        self.handler = CustomFTPHandler
        self.server: Optional[FTPServer] = None
        self.executor = ThreadPoolExecutor(max_workers=4)
        
        # 配置日志
        logging.basicConfig(
            filename='ftp_server.log',
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    async def start(self, host: str = "127.0.0.1", port: int = 2121):
        """
        异步启动FTP服务器
        
        参数:
            host: 服务器地址
            port: 服务器端口
        """
        try:
            # 确保基础目录存在
            os.makedirs(settings.FILE_SERVER_BASE_DIR, exist_ok=True)
            
            # 配置FTP处理器
            self.handler.authorizer = self.authorizer
            self.handler.banner = "人脸识别签到系统FTP服务器"
            
            # 创建FTP服务器
            self.server = FTPServer((host, port), self.handler)
            
            # 设置最大连接数
            self.server.max_cons = 256
            self.server.max_cons_per_ip = 5
            
            # 在事件循环中启动服务器
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, self.server.serve_forever)
            
        except Exception as e:
            logging.error(f"FTP服务器启动失败: {str(e)}")
            raise

    async def stop(self):
        """异步停止FTP服务器"""
        if self.server:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, self.server.close_all)
            self.executor.shutdown(wait=True)

    async def add_user(self, username: str, password: str, directory: str, permissions: str = "elradfmw"):
        """
        异步添加FTP用户
        
        参数:
            username: 用户名
            password: 密码
            directory: 用户目录
            permissions: 权限
        """
        try:
            # 确保用户目录存在
            os.makedirs(directory, exist_ok=True)
            
            # 在事件循环中添加用户
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(
                self.executor,
                self.authorizer.add_user,
                username,
                password,
                directory,
                permissions
            )
            logging.info(f"添加FTP用户成功: {username}")
        except Exception as e:
            logging.error(f"添加FTP用户失败: {str(e)}")
            raise

    async def remove_user(self, username: str):
        """
        异步删除FTP用户
        
        参数:
            username: 用户名
        """
        try:
            loop = asyncio.get_event_loop()
            await loop.run_in_executor(self.executor, self.authorizer.remove_user, username)
            logging.info(f"删除FTP用户成功: {username}")
        except Exception as e:
            logging.error(f"删除FTP用户失败: {str(e)}")
            raise

# 创建FTP服务实例
ftp_service = FTPService() 