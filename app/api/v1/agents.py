from fastapi import APIRouter

router = APIRouter()

@router.get("/agents")
async def get_agents():
    """
    Get list of all agents
    """
    return {"status": "ok"}