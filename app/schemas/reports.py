import uuid
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class Report(BaseModel):
    id: uuid.UUID
    results: dict
    created_at: datetime


class ReportCreate(BaseModel):
    jobs_ids: List[uuid.UUID]


class ReportUpdate(BaseModel):
    results: Optional[dict] = None
    jobs_ids: Optional[List[uuid.UUID]] = None
