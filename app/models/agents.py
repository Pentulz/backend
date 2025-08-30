import datetime
import enum
import uuid
from typing import List, Optional

from sqlalchemy import DateTime, Index, PrimaryKeyConstraint, Text, Uuid, text
from sqlalchemy.dialects.postgresql import ENUM, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class PlatformType(str, enum.Enum):
    WINDOWS = "WINDOWS"
    MACOS = "MACOS"
    LINUX = "LINUX"


class Agents(Base):
    __tablename__ = "agents"
    __table_args__ = (
        PrimaryKeyConstraint("id", name="agents_pkey"),
        Index("idx_agents_last_seen", "last_seen_at"),
        Index("idx_agents_platform", "platform"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, server_default=text("gen_random_uuid()")
    )
    hostname: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    platform: Mapped[PlatformType] = mapped_column(
        ENUM(PlatformType, name="platform_type", native_enum=True)
    )
    available_tools: Mapped[dict] = mapped_column(JSONB)
    token: Mapped[str] = mapped_column(Text)
    last_seen_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(
        DateTime, server_default=text("CURRENT_TIMESTAMP")
    )

    jobs: Mapped[List["Jobs"]] = relationship("Jobs", back_populates="agent")  # type: ignore
