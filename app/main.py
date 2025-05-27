from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import auth, attendance, statistics, student, user_management
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["认证"])
app.include_router(attendance.router, prefix=f"{settings.API_V1_STR}/attendance", tags=["考勤"])
app.include_router(statistics.router, prefix=f"{settings.API_V1_STR}/statistics", tags=["统计"])
app.include_router(student.router, prefix=f"{settings.API_V1_STR}/student", tags=["学生"])
app.include_router(user_management.router, prefix=f"{settings.API_V1_STR}/users", tags=["用户管理"])

@app.get("/")
async def root():
    return {"message": "人脸识别签到系统API"} 

if __name__=="__main__":
    import uvicorn
    uvicorn.run(app, host='192.168.224.98', port=8888)
    
#python -m app.main