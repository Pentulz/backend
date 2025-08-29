from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import CreateError, DeleteError, UpdateError
from app.schemas.agents import Agent, AgentCreate, AgentUpdate
from app.schemas.jobs import Job
from app.schemas.response import (
    create_error_response,
    create_success_response,
    create_success_response_list,
)
from app.services.agents import AgentsService
from app.utils.uuid import cast_uuid

router = APIRouter()


@router.get("/agents")
async def get_agents(db: AsyncSession = Depends(get_db)):
    """Get list of all agents with their jobs"""
    agents_service = AgentsService(db)
    agents = await agents_service.get_agents()

    if not agents:
        return create_success_response_list("agents", [])

    response = []
    for agent in agents:
        response.append(
            Agent(
                id=agent.id,
                hostname=agent.hostname,
                description=agent.description,
                platform=agent.platform,
                available_tools=agent.available_tools or [],
                token=agent.token,
                last_seen_at=agent.last_seen_at,
                created_at=agent.created_at,
                jobs=[
                    Job(
                        id=job.id,
                        name=job.name,
                        action=job.action,
                        agent_id=job.agent_id,
                        description=job.description,
                        results=job.results,
                        started_at=job.started_at,
                        completed_at=job.completed_at,
                        created_at=job.created_at,
                    ).model_dump(mode="json")
                    for job in agent.jobs
                ],
            ).model_dump(mode="json")
        )

    return create_success_response_list("agents", response)


@router.patch("/agents/{agent_id}")
async def update_agent(
    agent_id: str, agent: AgentUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Update an agent
    """
    if not cast_uuid(agent_id):
        error_msg = f"Invalid agent id: {agent_id}"
        return create_error_response("400", "Bad Request", error_msg, 400)

    try:
        agent_service = AgentsService(db)
        agent_from_db = await agent_service.update_agent(agent_id, agent)

        updated_agent = Agent(
            id=agent_from_db.id,
            hostname=agent_from_db.hostname,
            description=agent_from_db.description,
            platform=agent_from_db.platform,
            available_tools=agent_from_db.available_tools,
            token=agent_from_db.token,
            last_seen_at=agent_from_db.last_seen_at,
            created_at=agent_from_db.created_at,
        )

        response_json = updated_agent.model_dump(mode="json")
        return create_success_response("agents", str(agent_id), response_json)

    except UpdateError as e:
        return create_error_response("400", "Bad Request", str(e), 400)
    except Exception as e:
        return create_error_response("500", "Internal Server Error", str(e), 500)


@router.get("/agents/{agent_id}")
async def get_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get agent by id with jobs
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
        jobs=[
            Job(
                id=j.id,
                name=j.name,
                action=j.action,
                agent_id=j.agent_id,
                description=j.description,
                results=j.results,
                started_at=j.started_at if j.started_at else None,
                completed_at=j.completed_at if j.completed_at else None,
                created_at=j.created_at,
            )
            for j in (agent.jobs or [])
        ],
    )

    return create_success_response(
        "agents", str(agent_id), response.model_dump(mode="json")
    )


@router.post("/agents")
async def create_agent(agent: AgentCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new agent
    """
    try:
        agent_service = AgentsService(db)
        new_agent = await agent_service.create_agent(agent)

        response = Agent(
            id=new_agent.id,
            hostname=new_agent.hostname,
            description=new_agent.description,
            platform=new_agent.platform,
            available_tools=new_agent.available_tools,
            token=new_agent.token,
            last_seen_at=new_agent.last_seen_at,
            created_at=new_agent.created_at,
        )

        return create_success_response(
            "agents", str(new_agent.id), response.model_dump(mode="json")
        )
    except CreateError as e:
        return create_error_response("400", "Bad Request", str(e), 400)


@router.delete("/agents/{agent_id}")
async def delete_agent(agent_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete an agent
    """
    if not cast_uuid(agent_id):
        return create_error_response("400", "Bad Request", "Invalid agent id", 400)

    try:
        agent_service = AgentsService(db)
        await agent_service.delete_agent(agent_id)

        return create_success_response(
            "agents", str(agent_id), {"message": "Agent deleted"}
        )
    except DeleteError:
        return create_error_response("404", "Not Found", "Agent not found", 404)


@router.get("/agents/{agent_id}/jobs")
async def get_agent_jobs(
    agent_id: str, completed: bool = False, db: AsyncSession = Depends(get_db)
):
    """
    Get jobs for an agent if query params ?completed=false, return only not completed jobs
    Example:
    - GET http://localhost:8000/api/v1/agents/550e8400-e29b-41d4-a716-446655440001/jobs?completed=false
    - GET http://localhost:8000/api/v1/agents/550e8400-e29b-41d4-a716-446655440001/jobs?completed=true
    """
    if not cast_uuid(agent_id):
        return create_error_response("400", "Bad Request", "Invalid agent id", 400)

    agent_service = AgentsService(db)
    jobs = await agent_service.get_jobs_by_agent_id(agent_id, completed)

    if not jobs:
        return create_success_response_list("jobs", [])

    response = [
        Job(
            id=job.id,
            name=job.name,
            action=job.action,
            agent_id=job.agent_id,
            description=job.description,
            results=job.results,
            started_at=job.started_at,
            completed_at=job.completed_at,
            created_at=job.created_at,
        ).model_dump(mode="json")
        for job in jobs
    ]

    return create_success_response_list("jobs", response)
