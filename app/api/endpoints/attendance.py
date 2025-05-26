from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_attendance():
    return {"message": "考勤功能待实现"} 