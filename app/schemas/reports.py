import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

# Request models


class Report(BaseModel):
    id: uuid.UUID
    results: dict
    created_at: datetime


class ReportCreate(BaseModel):
    jobs_ids: List[uuid.UUID]


class ReportUpdate(BaseModel):
    results: Optional[dict] = None
    jobs_ids: Optional[List[uuid.UUID]] = None


# Response models


class ReportAttributes(BaseModel):
    """Report attributes for response model"""

    results: dict = Field(..., description="Report results")
    created_at: str = Field(..., description="When report was created (ISO format)")
    jobs_ids: List[str] | None = Field(
        None, description="List of job IDs included in report"
    )


class ReportResponse(BaseModel):
    """Response model for single report endpoint"""

    data: ReportAttributes = Field(..., description="Report data in JSON:API format")


class ReportsListResponse(BaseModel):
    """Response model for reports list endpoint"""

    data: List[ReportAttributes] = Field(
        ..., description="List of reports in JSON:API format"
    )
