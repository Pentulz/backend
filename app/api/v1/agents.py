from fastapi import APIRouter

router = APIRouter()


@router.get("/agents")
async def get_agents():
    """
    Get list of all agents
    """
    return {"status": "ok"}


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """
    Get agent by id
    """
    return {"status": "ok"}


@router.get("/agents/{agent_id}/jobs")
async def get_agent_jobs(agent_id: str):
    """
    Get jobs for an agent
    """
    return {"status": "ok"}


@router.post("/agents/{agent_id}")
async def create_agent_capabilities(agent_id: str):
    """
    Create an agent
    """
    return {"status": "ok"}


@router.patch("/agents/{agent_id}")
async def create_agent_capabilities(agent_id: str):
    """
    Update an agent (usually, update its capabilities)
    """
    return {"status": "ok"}
