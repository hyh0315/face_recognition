from fastapi import APIRouter

router = APIRouter()
 
@router.get("/")
async def get_statistics():
    return {"message": "统计功能待实现"} 