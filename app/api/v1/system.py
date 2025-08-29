from fastapi import APIRouter

from app.schemas.response import create_success_response_list
from app.services.tools.manager import ToolManager

router = APIRouter()


@router.get("/tools")
async def get_tools():
    """
    Get list of all supported penetration testing tools
    """
    manager = ToolManager()
    tools = manager.get_available_tools()

    return create_success_response_list("tools", tools)
