from fastapi import APIRouter

from app.core.response import create_success_response_list
from app.schemas.response_models import DetailedInternalServerError, ToolsResponse
from app.services.tools.manager import ToolManager

router = APIRouter()


@router.get(
    "/tools",
    response_model=ToolsResponse,
    responses={
        200: {"description": "List of tools retrieved successfully"},
        500: {
            "model": DetailedInternalServerError,
            "description": "Internal server error",
        },
    },
)
async def get_tools():
    """
    Get list of all supported penetration testing tools
    """
    manager = ToolManager()
    tools = manager.get_available_tools()

    return create_success_response_list("tools", tools)
