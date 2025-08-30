import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

# Request models


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


# Response models


class JobAttributes(BaseModel):
    """Job attributes for response model"""

    name: str = Field(..., description="Name of the job")
    action: dict = Field(..., description="Action to perform")
    agent_id: str = Field(..., description="ID of the agent")
    description: str | None = Field(None, description="Job description")
    results: dict | None = Field(None, description="Job results")
    started_at: str | None = Field(
        None, description="When the job started (ISO format)"
    )
    completed_at: str | None = Field(
        None, description="When the job completed (ISO format)"
    )
    created_at: str = Field(..., description="When the job was created (ISO format)")


class JobResponse(BaseModel):
    """Response model for single job endpoint"""

    data: JobAttributes = Field(..., description="Job data in JSON:API format")


class JobsListResponse(BaseModel):
    """Response model for jobs list endpoint"""

    data: List[JobAttributes] = Field(
        ..., description="List of jobs in JSON:API format"
    )
