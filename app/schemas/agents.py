import uuid
from datetime import datetime
from enum import Enum

from app.schemas.jobs import Job
from app.schemas.utc_datetime import UTCDatetime
from pydantic import BaseModel


class PlatformType(str, Enum):
    WINDOWS = "WINDOWS"
    MACOS = "MACOS"
    LINUX = "LINUX"


class Tool(BaseModel):
    cmd: str
    args: list[str] = []
    version: str | None


class Agent(BaseModel):
    id: uuid.UUID
    hostname: str | None
    description: str
    platform: PlatformType | None
    available_tools: list[Tool] | None
    token: str
    last_seen_at: UTCDatetime
    created_at: UTCDatetime
    jobs: list[Job] = []


class AgentCreate(BaseModel):
    hostname: str
    description: str


class AgentUpdate(BaseModel):
    hostname: str
    description: str
    platform: PlatformType
    available_tools: list[Tool]
    token: str
    last_seen_at: UTCDatetime
