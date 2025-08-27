from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.agents import Agent
from app.schemas.reponse import (
    create_error_response,
    create_success_response,
    create_success_response_list,
)
from app.services.agents_service import AgentsService
from app.utils.uuid import cast_uuid

router = APIRouter()


@router.get("/agents")
async def get_agents(db: AsyncSession = Depends(get_db)):
    """Get list of all agents"""
    agent_service = AgentsService(db)
    agents = await agent_service.get_agents()

    if not agents:
        return create_error_response("404", "Not Found", "No agents found", 404)

    response = [
        Agent(
            id=agent.id,
            hostname=agent.hostname,
            description=agent.description,
            platform=agent.platform,
            available_tools=agent.available_tools,
            token=agent.token,
            last_seen_at=agent.last_seen_at,
            created_at=agent.created_at,
        ).model_dump(mode="json")
        for agent in agents
    ]

    return create_success_response_list("agents", response)


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get agent by id
    """

    if not cast_uuid(agent_id):
        return create_error_response("400", "Bad Request", "Invalid agent id", 400)

    agent_service = AgentsService(db)
    agent = await agent_service.get_agent_by_id(agent_id)

    if not agent:
        return create_error_response("404", "Not Found", "Agent not found", 404)

    response = Agent(
        id=agent.id,
        hostname=agent.hostname,
        description=agent.description,
        platform=agent.platform,
        available_tools=agent.available_tools,
        token=agent.token,
        last_seen_at=agent.last_seen_at,
        created_at=agent.created_at,
    )

    return create_success_response(
        "agents", str(agent_id), response.model_dump(mode="json")
    )


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
