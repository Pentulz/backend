import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

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


class AgentUpdate(BaseModel):
    hostname: Optional[str] = None
    description: Optional[str] = None
    platform: Optional[PlatformType] = None
    available_tools: Optional[dict] = None
    token: Optional[str] = None
    last_seen_at: Optional[datetime] = None
