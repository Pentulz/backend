from fastapi import APIRouter

router = APIRouter()

@router.get("/jobs")
async def get_jobs():
    """
    Get list of all jobs
    """
    return {"status": "ok"}