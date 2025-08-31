import uuid
from datetime import datetime
from typing import Any, Dict, Optional, Union

from pydantic import BaseModel, Field, validator


class JobAction(BaseModel):
    """Schema for job action using tool templates"""

    name: str = Field(..., description="Tool name (e.g., 'nmap', 'ffuf')")
    variant: str = Field(
        ..., description="Template ID (e.g., 'tcp_connect_scan', 'directory_fuzzing')"
    )
    args: Dict[str, Any] = Field(..., description="Custom arguments for the template")

    @validator("name")
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError("Tool name cannot be empty")
        return v.strip()

    @validator("variant")
    def validate_variant(cls, v):
        if not v or not v.strip():
            raise ValueError("Template variant cannot be empty")
        return v.strip()

    @validator("args")
    def validate_args(cls, v):
        if not isinstance(v, dict):
            raise ValueError("Args must be a dictionary")
        return v


class JobActionResponse(BaseModel):
    """Schema for job action response - can handle both original args and built command"""

    name: str = Field(..., description="Tool name (e.g., 'nmap', 'ffuf')")
    variant: str = Field(
        ..., description="Template ID (e.g., 'tcp_connect_scan', 'directory_fuzzing')"
    )
    args: Union[Dict[str, Any], list] = Field(
        ..., description="Custom arguments or built command"
    )


# Request models


class Job(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    agent_id: uuid.UUID
    action: JobActionResponse
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    results: Optional[str] = None


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
    results: Optional[str] = None

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
    description: Optional[str] = Field(None, description="Job description")
    results: Optional[str] = Field(None, description="Job results (raw tool output)")
    started_at: Optional[str] = Field(
        None, description="When the job started (ISO format)"
    )
    completed_at: Optional[str] = Field(
        None, description="When the job completed (ISO format)"
    )
    created_at: str = Field(..., description="When the job was created (ISO format)")


class JobResponse(BaseModel):
    """Response model for single job endpoint"""

    data: JobAttributes = Field(..., description="Job data in JSON:API format")


class JobsListResponse(BaseModel):
    """Response model for jobs list endpoint"""

    data: list[JobAttributes] = Field(
        ..., description="List of jobs in JSON:API format"
    )
