from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.jobs import Jobs
from app.models.reports import Reports
from app.schemas.reports import ReportCreate


class ReportsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_reports(self) -> List[Reports]:
        query = select(Reports)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_report_by_id(self, report_id: str) -> Optional[Reports]:
        query = select(Reports).where(Reports.id == report_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_report(self, report: ReportCreate) -> Reports:
        # Get jobs
        jobs = await self.db.execute(select(Jobs).where(Jobs.id.in_(report.jobs_ids)))
        jobs = jobs.scalars().all()

        # Get results
        results = [job.results for job in jobs]

        # Create report
        new_report = Reports(results=results, jobs_ids=report.jobs_ids)

        self.db.add(new_report)
        await self.db.commit()

        return new_report
