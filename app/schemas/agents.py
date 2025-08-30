import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel

from app.schemas.jobs import Job


class PlatformType(str, Enum):
    WINDOWS = "WINDOWS"
    MACOS = "MACOS"
    LINUX = "LINUX"


class Tool(BaseModel):
    cmd: str
    args: list[str] = []
    version: str | None
    version_arg: str | None


class Agent(BaseModel):
    id: uuid.UUID
    hostname: str | None
    description: str
    platform: PlatformType | None
    available_tools: list[Tool] | None
    token: str
    last_seen_at: datetime
    created_at: datetime
    jobs: list[Job] = []


class AgentCreate(BaseModel):
    name: str
    description: str


class AgentUpdate(BaseModel):
    hostname: str
    description: str
    platform: PlatformType
    available_tools: list[Tool] | None
    token: str
    last_seen_at: datetime
