from app.utils.auth import verify_agent_token
from fastapi import APIRouter, Depends, Header, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine

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
from app.schemas.jobs import (
    Job,
    JobActionResponse,
    JobCreate,
    JobResponse,
    JobsListResponse,
    JobUpdate,
)
from app.schemas.jobs import Job, JobActionResponse, JobsListResponse
from app.schemas.response_models import (
    DetailedBadRequestError,
    DetailedInternalServerError,
    DetailedNotFoundError,
    MessageResponse,
)
from app.services.agents import AgentsService
from app.services.jobs import JobsService
from app.services.tools.tool_manager import ToolManager
from app.utils.uuid import cast_uuid


router = APIRouter()

@router.get(
    "/self",
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
async def get_agent(
    agent=Depends(verify_agent_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Get agent by id with jobs
    """
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
        jobs=[],
    )

    return create_success_response(
        "agents", str(agent.id), response.model_dump(mode="json")
    )


@router.patch(
    "/self",
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
    agent_register: AgentUpdate,
    agent=Depends(verify_agent_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an agent
    """

    try:
        agent_service = AgentsService(db)

        agent_from_db = await agent_service.update_agent(agent.id, agent_register)

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
        return create_success_response("agents", str(agent.id), response_json)

    except UpdateError as e:
        return create_error_response("400", "Bad Request", str(e), 400)
    except Exception as e:
        return create_error_response("500", "Internal Server Error", str(e), 500)


@router.get(
    "/jobs",
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
    agent=Depends(verify_agent_token),
    db: AsyncSession = Depends(get_db),
):
    """ """

    completed = False
    agent_service = AgentsService(db)
    jobs = await agent_service.get_jobs_by_agent_id(agent.id, completed)

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

    return create_success_response_list("jobs", response)


@router.patch(
    "/jobs/{job_id}",
    response_model=JobResponse,
    responses={
        200: {"description": "Job updated successfully"},
        400: {
            "model": DetailedBadRequestError,
            "description": "Bad request - invalid data",
        },
        404: {"model": DetailedNotFoundError, "description": "Job not found"},
        500: {
            "model": DetailedInternalServerError,
            "description": "Internal server error",
        },
    },
)
async def update_job(
    job_id: str,
    job: JobUpdate,
    agent=Depends(verify_agent_token),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a job
    """
    if not cast_uuid(job_id):
        return create_error_response("400", "Bad Request", "Invalid job id", 400)

    try:
        jobs_service = JobsService(db)
        job = await jobs_service.update_job(job_id, job)

        response = Job(
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
            success=job.success,
        )

        return create_success_response(
            "jobs", str(job.id), response.model_dump(mode="json")
        )
    except UpdateError as e:
        return create_error_response(
            "422",
            "Unprocessable Entity",
            str(e),
            422,
        )
