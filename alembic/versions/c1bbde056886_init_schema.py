"""init schema

Revision ID: c1bbde056886
Revises:
Create Date: 2025-09-05 07:38:15.970609
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c1bbde056886"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Create platform enum
    op.execute("CREATE TYPE platform_type AS ENUM ('WINDOWS', 'MACOS', 'LINUX')")

    # Create agents table
    op.execute("""
        CREATE TABLE agents (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            hostname TEXT NULL,
            description TEXT,
            platform platform_type NULL,
            available_tools JSONB NULL,
            token TEXT NOT NULL,
            last_seen_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT unique_agent_name UNIQUE (name),
            CONSTRAINT unique_agent_hostname UNIQUE (hostname)
        )
    """)

    # Create jobs table
    op.execute("""
        CREATE TABLE jobs (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            agent_id UUID REFERENCES agents(id) ON DELETE SET NULL,
            name TEXT NOT NULL,
            description TEXT,
            action JSONB NOT NULL,
            results TEXT,
            success BOOLEAN DEFAULT NULL,
            started_at TIMESTAMP WITH TIME ZONE NULL,
            completed_at TIMESTAMP WITH TIME ZONE NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create reports table
    op.execute("""
        CREATE TABLE reports (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            name TEXT NOT NULL,
            description TEXT,
            results JSONB NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create junction table for many-to-many between jobs and reports
    op.execute("""
        CREATE TABLE reports_jobs (
            job_id UUID REFERENCES jobs(id) ON DELETE CASCADE,
            report_id UUID REFERENCES reports(id) ON DELETE CASCADE,
            PRIMARY KEY (job_id, report_id)
        )
    """)

    # Create indexes
    op.execute("CREATE INDEX idx_agents_last_seen ON agents(last_seen_at)")
    op.execute("CREATE INDEX idx_agents_platform ON agents(platform)")
    op.execute("CREATE INDEX idx_jobs_agent_id ON jobs(agent_id)")
    op.execute("CREATE INDEX idx_jobs_created_at ON jobs(created_at)")
    op.execute("CREATE INDEX idx_reports_created_at ON reports(created_at)")
    op.execute("CREATE INDEX idx_reports_jobs_job_id ON reports_jobs(job_id)")
    op.execute("CREATE INDEX idx_reports_jobs_report_id ON reports_jobs(report_id)")


def downgrade() -> None:
    """Downgrade schema."""

    # Drop indexes
    op.execute("DROP INDEX IF EXISTS idx_reports_jobs_report_id")
    op.execute("DROP INDEX IF EXISTS idx_reports_jobs_job_id")
    op.execute("DROP INDEX IF EXISTS idx_reports_created_at")
    op.execute("DROP INDEX IF EXISTS idx_jobs_created_at")
    op.execute("DROP INDEX IF EXISTS idx_jobs_agent_id")
    op.execute("DROP INDEX IF EXISTS idx_agents_platform")
    op.execute("DROP INDEX IF EXISTS idx_agents_last_seen")

    # Drop tables
    op.execute("DROP TABLE IF EXISTS reports_jobs")
    op.execute("DROP TABLE IF EXISTS reports")
    op.execute("DROP TABLE IF EXISTS jobs")
    op.execute("DROP TABLE IF EXISTS agents")

    # Drop enum
    op.execute("DROP TYPE IF EXISTS platform_type")
