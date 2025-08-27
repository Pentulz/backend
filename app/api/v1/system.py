from fastapi import APIRouter

router = APIRouter()


@router.get("/tools")
async def get_tools():
    """
    Get list of all supported penetration testing tools
    """
    return {"status": "ok"}
