from sqlalchemy import Column, ForeignKeyConstraint, Index, PrimaryKeyConstraint, Table, Uuid
from app.core.database import Base


t_reports_jobs = Table(
    'reports_jobs', Base.metadata,
    Column('job_id', Uuid, primary_key=True, nullable=False),
    Column('report_id', Uuid, primary_key=True, nullable=False),
    ForeignKeyConstraint(['job_id'], ['jobs.id'], ondelete='CASCADE', name='reports_jobs_job_id_fkey'),
    ForeignKeyConstraint(['report_id'], ['reports.id'], ondelete='CASCADE', name='reports_jobs_report_id_fkey'),
    PrimaryKeyConstraint('job_id', 'report_id', name='reports_jobs_pkey'),
    Index('idx_reports_jobs_job_id', 'job_id'),
    Index('idx_reports_jobs_report_id', 'report_id')
)
