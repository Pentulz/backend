from fastapi import APIRouter

router = APIRouter()


@router.get("/tools")
async def get_tools():
    """
    Get list of all supported penetration testing tools
    """
    
    # TODO : Get tools from backend
    
    return {
        "tools": {
            "nmap": "7.93",
            "tshark": "5.0.0",
            "ffuf": "2.1.0",
        }
    }
