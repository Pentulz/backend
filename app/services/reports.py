from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CreateError, DeleteError, UpdateError
from app.models.jobs import Jobs
from app.models.reports import Reports
from app.schemas.reports import ReportCreate, ReportUpdate
from app.services.tools.manager import ToolManager


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
        if not report.jobs_ids:
            raise CreateError("Jobs ids are required")

        # Get jobs
        jobs = await self.db.execute(select(Jobs).where(Jobs.id.in_(report.jobs_ids)))
        jobs = jobs.scalars().all()

        # Get results
        for job in jobs:
            tool_name = job.action.get("tool")
            tool_manager = ToolManager()
            tool = tool_manager.get_tool(tool_name)
            results = tool.parse_results(job.results, job.action.get("command"))

        # Process results
        processed_results = results

        # Create report
        new_report = Reports(results=processed_results, jobs_ids=report.jobs_ids)

        try:
            self.db.add(new_report)
            await self.db.commit()
        except IntegrityError as e:
            raise CreateError(f"Failed to create report: {e}") from e

        return new_report

    async def update_report(
        self, report_id: str, report_update: ReportUpdate
    ) -> Reports:
        report = await self.get_report_by_id(report_id)
        if not report:
            raise UpdateError("Report not found")

        if report_update.results is not None:
            report.results = report_update.results
        if report_update.jobs_ids is not None:
            # Get jobs
            jobs = await self.db.execute(
                select(Jobs).where(Jobs.id.in_(report_update.jobs_ids))
            )
            jobs = jobs.scalars().all()

            # Get results
            results = [job.results for job in jobs]

            # Process results
            processed_results = results

            report.results = processed_results

        try:
            self.db.add(report)
            await self.db.commit()
        except IntegrityError as e:
            raise UpdateError(f"Failed to update report: {e}") from e

        return report

    async def delete_report(self, report_id: str) -> None:
        report = await self.get_report_by_id(report_id)
        if not report:
            raise DeleteError("Report not found")

        try:
            await self.db.delete(report)
            await self.db.commit()
        except IntegrityError as e:
            raise DeleteError(f"Failed to delete report: {e}") from e
