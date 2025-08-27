import uuid
from datetime import datetime

from pydantic import BaseModel


class Report(BaseModel):
    id: uuid.UUID
    results: dict
    created_at: datetime


class ReportCreate(BaseModel):
    jobs_ids: list[uuid.UUID]
