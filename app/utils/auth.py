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


async def verify_agent_token(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )

    token = authorization[len("Bearer ") :]
    agent_service = AgentsService(db)
    agent = await agent_service.get_agent_by_token(token)
    if agent is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid agent token",
        )

    return agent
