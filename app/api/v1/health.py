from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response"""

    status: str = "ok"


@router.get(
    "/health",
    response_model=HealthResponse,
    responses={200: {"description": "Health check successful"}},
)
async def get_health():
    """
    Get health of the system
    """

    return {"status": "ok"}
