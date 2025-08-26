from fastapi import APIRouter

router = APIRouter()

@router.get("/reports")
async def get_reports():
    """
    Get list of all reports
    """
    return {"status": "ok"}