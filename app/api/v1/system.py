from fastapi import APIRouter

from app.schemas.response import create_success_response_list

router = APIRouter()


@router.get("/tools")
async def get_tools():
    """
    Get list of all supported penetration testing tools
    """

    # TODO : Get tools from backend

    tools = [
        {
            "id": "tool1",
            "cmd": "nmap",
            "args": ["-sV", "127.0.0.1"],
            "version_arg": "--version",
        },
        {
            "id": "tool2",
            "cmd": "gobuster",
            "args": [
                "dir",
                "-u",
                "http://localhost",
                "-w",
                "/wordlists/common.txt",
            ],
            "version_arg": "--version",
        },
        {
            "id": "tool3",
            "cmd": "tcpdump",
            "args": ["-i", "eth0", "-c", "10"],
            "version_arg": "--version",
        },
    ]

    return create_success_response_list("tools", tools)
