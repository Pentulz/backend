import uuid
from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel, Field, validator


# Action schema for job actions
class JobAction(BaseModel):
    """Schema for job action validation"""

    cmd: str = Field(..., description="Tool command to execute")
    args: List[str] = Field(..., description="Command arguments")
    timeout: Union[int, float] = Field(300, ge=0, description="Timeout in seconds")

    @validator("cmd")
    def validate_cmd(cls, v):
        if not v or not v.strip():
            raise ValueError("Command cannot be empty")
        return v.strip()

    @validator("args")
    def validate_args(cls, v):
        if not v:
            raise ValueError("Args cannot be empty")

        if not all(isinstance(arg, str) for arg in v):
            raise ValueError("All args must be strings")
        return v

    @validator("timeout")
    def validate_timeout(cls, v):
        if v < 0:
            raise ValueError("Timeout must be non-negative")
        return v


# Request models


class Job(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    agent_id: uuid.UUID
    action: JobAction
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    results: Optional[dict] = None


class JobCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Job name")
    description: Optional[str] = None
    agent_id: uuid.UUID = Field(..., description="Agent ID to execute the job")
    action: JobAction = Field(..., description="Action to perform")

    @validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @validator("description")
    def validate_description(cls, v):
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None


class JobUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    agent_id: Optional[uuid.UUID] = None
    action: Optional[JobAction] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    results: Optional[dict] = None

    @validator("name")
    def validate_name(cls, v):
        if v is not None and not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip() if v else None

    @validator("description")
    def validate_description(cls, v):
        if v is not None and not v.strip():
            return None
        return v.strip() if v else None


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
