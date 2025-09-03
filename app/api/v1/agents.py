from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import CreateError, DeleteError, UpdateError
from app.core.response import (
    create_error_response,
    create_success_response,
    create_success_response_list,
)
from app.schemas.agents import (
    Agent,
    AgentCreate,
    AgentResponse,
    AgentsListResponse,
    AgentUpdate,
)
from app.schemas.jobs import Job, JobActionResponse, JobsListResponse
from app.schemas.response_models import (
    DetailedBadRequestError,
    DetailedInternalServerError,
    DetailedNotFoundError,
    MessageResponse,
)
from app.services.agents import AgentsService
from app.services.tools.tool_manager import ToolManager
from app.utils.uuid import cast_uuid

router = APIRouter()


@router.get(
    "/agents",
    response_model=AgentsListResponse,
    responses={
        200: {"description": "List of agents retrieved successfully"},
        500: {
            "model": DetailedInternalServerError,
            "description": "Internal server error",
        },
    },
)
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
                name=agent.name,
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
                        action=JobActionResponse(
                            cmd=job.action["cmd"],
                            variant=job.action["variant"],
                            args=[str(v) for v in job.action["args"]],
                        ),
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


@router.patch(
    "/agents/{agent_id}",
    response_model=AgentResponse,
    responses={
        200: {"description": "Agent updated successfully"},
        400: {
            "model": DetailedBadRequestError,
            "description": "Bad request - invalid data",
        },
        404: {"model": DetailedNotFoundError, "description": "Agent not found"},
        500: {
            "model": DetailedInternalServerError,
            "description": "Internal server error",
        },
    },
)
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
            name=agent_from_db.name,
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


@router.get(
    "/agents/{agent_id}",
    response_model=AgentResponse,
    responses={
        200: {"description": "Agent retrieved successfully"},
        400: {
            "model": DetailedBadRequestError,
            "description": "Bad request - invalid agent ID",
        },
        404: {"model": DetailedNotFoundError, "description": "Agent not found"},
    },
)
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

    tool_manager = ToolManager()
    jobs = []

    for job in agent.jobs:
        action = job.action or {}
        cmd = action.get("cmd")
        args = action.get("args", [])

        if cmd:
            tool = tool_manager.get_tool(cmd)
            if tool:
                export_args = tool.export_arguments or []
                if export_args:
                    needs_append = True
                    if len(args) >= len(export_args):
                        if args[-len(export_args) :] == export_args:
                            needs_append = False
                    if needs_append:
                        args = list(args) + list(export_args)

        updated_action = {**action, "args": args}

        jobs.append(
            Job(
                id=job.id,
                name=job.name,
                # action=updated_action,
                action=JobActionResponse(
                    cmd=updated_action["cmd"],
                    variant=updated_action["variant"],
                    args=[str(v) for v in updated_action["args"]],
                ),
                agent_id=job.agent_id,
                description=job.description,
                results=job.results,
                started_at=job.started_at,
                completed_at=job.completed_at,
                created_at=job.created_at,
                success=job.success,
            ).model_dump(mode="json")
        )

    response = Agent(
        id=agent.id,
        name=agent.name,
        hostname=agent.hostname,
        description=agent.description,
        platform=agent.platform,
        available_tools=agent.available_tools,
        token=agent.token,
        last_seen_at=agent.last_seen_at,
        created_at=agent.created_at,
        jobs=jobs,
    )

    return create_success_response(
        "agents", str(agent_id), response.model_dump(mode="json")
    )


@router.post(
    "/agents",
    response_model=AgentResponse,
    responses={
        200: {"description": "Agent created successfully"},
        400: {
            "model": DetailedBadRequestError,
            "description": "Bad request - invalid data",
        },
        500: {
            "model": DetailedInternalServerError,
            "description": "Internal server error",
        },
    },
)
async def create_agent(agent: AgentCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new agent
    """
    try:
        agent_service = AgentsService(db)
        new_agent = await agent_service.create_agent(agent)

        response = Agent(
            id=new_agent.id,
            name=new_agent.name,
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


@router.delete(
    "/agents/{agent_id}",
    response_model=MessageResponse,
    responses={
        200: {"description": "Agent deleted successfully"},
        400: {
            "model": DetailedBadRequestError,
            "description": "Bad request - invalid agent ID",
        },
        404: {"model": DetailedNotFoundError, "description": "Agent not found"},
    },
)
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


@router.get(
    "/agents/{agent_id}/jobs",
    response_model=JobsListResponse,
    responses={
        200: {"description": "Agent jobs retrieved successfully"},
        400: {
            "model": DetailedBadRequestError,
            "description": "Bad request - invalid agent ID",
        },
    },
)
async def get_agent_jobs(
    agent_id: str, completed: bool = False, db: AsyncSession = Depends(get_db)
):
    """
    Get jobs for an agent if query params ?completed=false, return only not completed jobs
    Example:
    - GET http://localhost:8000/api/v1/agents/<agent_id>/jobs?completed=false
    - GET http://localhost:8000/api/v1/agents/<agent_id>/jobs?completed=true
    """
    if not cast_uuid(agent_id):
        return create_error_response("400", "Bad Request", "Invalid agent id", 400)

    agent_service = AgentsService(db)
    jobs = await agent_service.get_jobs_by_agent_id(agent_id, completed)

    if not jobs:
        return create_success_response_list("jobs", [])

    tool_manager = ToolManager()

    response = []
    for job in jobs:
        action = job.action or {}
        cmd = action.get("cmd")
        args = action.get("args", [])

        if cmd:
            tool = tool_manager.get_tool(cmd)
            if tool:
                export_args = tool.export_arguments or []
                if export_args:
                    needs_append = True
                    if len(args) >= len(export_args):
                        if args[-len(export_args) :] == export_args:
                            needs_append = False
                    if needs_append:
                        args = list(args) + list(export_args)

        updated_action = {**action, "args": args}

        response.append(
            Job(
                id=job.id,
                name=job.name,
                action=updated_action,
                agent_id=job.agent_id,
                description=job.description,
                results=job.results,
                started_at=job.started_at,
                completed_at=job.completed_at,
                created_at=job.created_at,
                success=job.success,
            ).model_dump(mode="json")
        )

    return create_success_response_list("jobs", response)
