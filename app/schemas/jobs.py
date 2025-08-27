import uuid
from datetime import datetime

from pydantic import BaseModel


class Job(BaseModel):
    id: uuid.UUID
    name: str
    description: str
    agent_id: str
    action: dict
    description: str
    created_at: datetime


class JobCreate(BaseModel):
    name: str
    description: str
    agent_id: str
    action: dict
