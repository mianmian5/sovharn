from fastapi import APIRouter
router = APIRouter()
@router.get("/audit/stats")
async def stats():
    return {"sessions": 0, "total_calls": 0}
