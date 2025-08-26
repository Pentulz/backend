from fastapi import APIRouter

router = APIRouter()

@router.get("/reports")
async def get_reports():
    """
    Get list of all reports
    """
    return {"status": "ok"}

@router.post("/reports")
async def create_report():
    """
    Create a new report
    """
    return {"status": "ok"}

@router.get("/reports/{report_id}")
async def get_report(report_id: str):
    """
    Get report by id
    """
    return {"status": "ok"}