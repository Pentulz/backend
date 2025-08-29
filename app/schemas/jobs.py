import uuid
from typing import Optional

from app.schemas.utc_datetime import UTCDatetime
from pydantic import BaseModel


class Job(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    agent_id: uuid.UUID
    action: dict
    started_at: Optional[UTCDatetime] = None
    completed_at: Optional[UTCDatetime] = None
    created_at: UTCDatetime
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
    started_at: Optional[UTCDatetime] = None
    completed_at: Optional[UTCDatetime] = None
    results: Optional[dict] = None
