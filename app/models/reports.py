import datetime
import uuid
from typing import List, Optional

from sqlalchemy import DateTime, Index, PrimaryKeyConstraint, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Reports(Base):
    __tablename__ = "reports"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="reports_pkey"),
        Index("idx_reports_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    results: Mapped[dict] = mapped_column(JSONB)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )

    job: Mapped[List["Jobs"]] = relationship("Jobs", secondary="reports_jobs", back_populates="report")  # type: ignore
