import uuid
from datetime import datetime
from enum import Enum
from typing import List

from pydantic import BaseModel, Field

from app.schemas.jobs import Job, JobAttributes


class PlatformType(str, Enum):
    WINDOWS = "WINDOWS"
    MACOS = "MACOS"
    LINUX = "LINUX"


class Tool(BaseModel):
    cmd: str
    args: list[str] = []
    version: str | None
    version_arg: str | None


# Request models


class Agent(BaseModel):
    id: uuid.UUID
    name: str
    hostname: str | None
    description: str
    platform: PlatformType | None
    available_tools: list[Tool] | None
    token: str
    last_seen_at: datetime | None
    created_at: datetime
    jobs: list[Job] = []


class AgentCreate(BaseModel):
    name: str
    description: str


class AgentUpdate(BaseModel):
    name: str | None = None
    hostname: str | None = None
    description: str | None = None
    platform: PlatformType | None = None
    available_tools: list[Tool] | None = None
    token: str | None = None
    last_seen_at: datetime | None = None


# Response models


class AgentAttributes(BaseModel):
    """Agent attributes for response model"""

    hostname: str = Field(..., description="Agent hostname")
    description: str | None = Field(None, description="Agent description")
    platform: str = Field(..., description="Operating system platform")
    available_tools: List[str] = Field(
        default_factory=list, description="List of available tools"
    )
    token: str = Field(..., description="Agent authentication token")
    last_seen_at: str | None = Field(
        None, description="Last time agent was seen (ISO format)"
    )
    created_at: str = Field(..., description="When agent was created (ISO format)")
    jobs: List[JobAttributes] | None = Field(None, description="List of agent jobs")


class AgentResponse(BaseModel):
    """Response model for single agent endpoint"""

    data: AgentAttributes = Field(..., description="Agent data in JSON:API format")


class AgentsListResponse(BaseModel):
    """Response model for agents list endpoint"""

    data: List[AgentAttributes] = Field(
        ..., description="List of agents in JSON:API format"
    )
