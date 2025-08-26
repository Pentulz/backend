from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def get_health():
    """
    Get health of the system
    """
    return {"status": "ok"}
