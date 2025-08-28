import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Job(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    agent_id: uuid.UUID
    action: dict
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    results: Optional[dict] = None


class JobCreate(BaseModel):
    name: str
    description: Optional[str] = None
    agent_id: uuid.UUID
    action: dict


class JobUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    agent_id: Optional[uuid.UUID] = None
    action: Optional[dict] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Optional[dict] = None
