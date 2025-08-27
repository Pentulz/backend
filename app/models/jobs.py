from typing import List, Optional

from sqlalchemy import DateTime, ForeignKeyConstraint, Index, PrimaryKeyConstraint, Text, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
import datetime
import uuid

from app.core.database import Base

class Jobs(Base):
    __tablename__ = 'jobs'
    __table_args__ = (
        ForeignKeyConstraint(['agent_id'], ['agents.id'], ondelete='SET NULL', name='jobs_agent_id_fkey'),
        PrimaryKeyConstraint('id', name='jobs_pkey'),
        Index('idx_jobs_agent_id', 'agent_id'),
        Index('idx_jobs_created_at', 'created_at')
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, server_default=text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(Text)
    action: Mapped[dict] = mapped_column(JSONB)
    agent_id: Mapped[Optional[uuid.UUID]] = mapped_column(Uuid)
    description: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    completed_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    agent: Mapped[Optional['Agents']] = relationship('Agents', back_populates='jobs') # type: ignore
    report: Mapped[List['Reports']] = relationship('Reports', secondary='reports_jobs', back_populates='job') # type: ignore