import uuid
from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class PlatformType(str, Enum):
    WINDOWS = "WINDOWS"
    MACOS = "MACOS"
    LINUX = "LINUX"


class Agent(BaseModel):
    id: uuid.UUID
    hostname: str
    description: str
    platform: PlatformType
    available_tools: dict
    token: str
    last_seen_at: datetime
    created_at: datetime


class AgentCreate(BaseModel):
    hostname: str
    description: str
