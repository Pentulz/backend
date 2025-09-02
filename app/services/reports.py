import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CreateError, DeleteError, UpdateError
from app.models.jobs import Jobs
from app.models.reports import Reports
from app.schemas.reports import ReportCreate, ReportUpdate
from app.services.tools.tool_manager import ToolManager


class ReportsService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.tool_manager = ToolManager()

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

        # Generate comprehensive security report
        report_data = await self._generate_security_report(report.jobs_ids, report.name)

        # Create report with name and description
        new_report = Reports(
            name=report.name, description=report.description, results=report_data
        )

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

        # Update name and description if provided
        if report_update.name is not None:
            report.name = report_update.name
        if report_update.description is not None:
            report.description = report_update.description

        if report_update.jobs_ids is not None:
            # Regenerate report with new jobs
            report_data = await self._generate_security_report(
                report_update.jobs_ids, report.name
            )
            report.results = report_data

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

    async def _generate_security_report(
        self, job_ids: List[str], report_name: str = "Security Assessment Report"
    ) -> Dict[str, Any]:
        """Generate a comprehensive security assessment report from job results"""
        # Get jobs by IDs
        jobs = await self._get_jobs_by_ids(job_ids)

        # Ensure JSON-serializable job ids for results metadata
        job_ids_as_strings = [str(j) for j in job_ids]

        findings_by_tool = {}
        all_findings = []

        # Process each job
        for job in jobs:
            tool_name = job.action.get("cmd", "unknown")
            raw_output = job.results if job.results else ""

            # Reconstruct command from new action format
            cmd = job.action.get("cmd", "")
            args = job.action.get("args", [])
            command = f"{cmd} {' '.join(args)}" if cmd and args else ""

            # Parse job results using appropriate tool parser
            parsed_result = await self._parse_job_results(
                tool_name,
                raw_output,
                command,
                str(job.agent_id) if job.agent_id else None,
            )

            if parsed_result and "findings" in parsed_result:
                # Group findings by tool
                if tool_name not in findings_by_tool:
                    findings_by_tool[tool_name] = {
                        "tool_name": tool_name.title(),
                        "jobs_count": 0,
                        "findings": [],
                        "statistics": {},
                    }

                findings_by_tool[tool_name]["jobs_count"] += 1
                findings_by_tool[tool_name]["findings"].extend(
                    parsed_result["findings"]
                )

                # Merge statistics
                if "statistics" in parsed_result:
                    for key, value in parsed_result["statistics"].items():
                        if key not in findings_by_tool[tool_name]["statistics"]:
                            findings_by_tool[tool_name]["statistics"][key] = value
                        elif isinstance(value, (int, float)):
                            findings_by_tool[tool_name]["statistics"][key] += value
                        elif isinstance(value, dict):
                            # Merge nested dictionaries (e.g., status code counts)
                            if key not in findings_by_tool[tool_name]["statistics"]:
                                findings_by_tool[tool_name]["statistics"][key] = {}
                            findings_by_tool[tool_name]["statistics"][key].update(value)

                all_findings.extend(parsed_result["findings"])

        # Generate report metadata
        report_id = str(uuid.uuid4())

        # Count findings by severity
        severity_counts = self._count_findings_by_severity(all_findings)

        # Calculate overall statistics
        total_jobs = len(jobs)
        total_findings = len(all_findings)

        # Format final report
        return {
            "metadata": {
                "report_id": report_id,
                "name": report_name,
                "created_at": datetime.now().isoformat(),
                "jobs_ids": job_ids_as_strings,
                "total_jobs": total_jobs,
                "total_findings": total_findings,
            },
            "summary": {
                "severity_distribution": severity_counts,
                "total_findings": total_findings,
                "tools_used": list(findings_by_tool.keys()),
            },
            "findings_by_tool": findings_by_tool,
            "all_findings": all_findings,
        }

    async def _get_jobs_by_ids(self, job_ids: List[str]) -> List[Jobs]:
        """Get jobs by their IDs"""
        query = select(Jobs).where(Jobs.id.in_(job_ids))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def _parse_job_results(
        self, tool_name: str, raw_output: str, command: str, agent_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """Parse job results using the appropriate tool parser"""
        try:
            # Get tool and parse results
            tool = self.tool_manager.get_tool(tool_name)
            if tool:
                return tool.parse_results(raw_output, command, agent_id)

            # Fallback for unknown tools
            return {
                "findings": [
                    {
                        "id": f"unknown_{tool_name}",
                        "title": f"Unknown Tool: {tool_name}",
                        "description": f"Results from unknown tool {tool_name}",
                        "target": "Unknown",
                        "severity": "info",
                        "agent_id": agent_id or "unknown",
                        "timestamp": datetime.now().isoformat(),
                    }
                ],
                "statistics": {"tool_name": tool_name, "status": "unknown_tool"},
            }
        except Exception as e:
            # Return error finding if parsing fails
            return {
                "findings": [
                    {
                        "id": f"error_{tool_name}",
                        "title": f"Parsing Error: {tool_name}",
                        "description": f"Failed to parse results from {tool_name}: {str(e)}",
                        "target": "Error",
                        "severity": "critical",
                        "agent_id": agent_id or "unknown",
                        "timestamp": datetime.now().isoformat(),
                    }
                ],
                "statistics": {
                    "tool_name": tool_name,
                    "status": "parsing_error",
                    "error": str(e),
                },
            }

    def _count_findings_by_severity(
        self, findings: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """Count findings by severity level"""
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}

        for finding in findings:
            severity = finding.get("severity", "info").lower()
            if severity in severity_counts:
                severity_counts[severity] += 1

        return severity_counts

    async def generate_custom_report(
        self, job_ids: List[str], report_name: str = None
    ) -> Dict[str, Any]:
        """Generate a custom report with specific formatting"""
        report_data = await self._generate_security_report(job_ids)

        if report_name:
            report_data["metadata"]["name"] = report_name

        return report_data

    async def get_report_summary(self, report_id: str) -> Optional[Dict[str, Any]]:
        """Get a summary of a specific report"""
        report = await self.get_report_by_id(report_id)
        if not report:
            return None

        results = report.results
        if not results:
            return None

        return {
            "report_id": str(report.id),
            "name": results.get("metadata", {}).get("name", "Unknown Report"),
            "created_at": results.get("metadata", {}).get("created_at"),
            "total_jobs": results.get("metadata", {}).get("total_jobs", 0),
            "total_findings": results.get("metadata", {}).get("total_findings", 0),
            "severity_summary": results.get("summary", {}).get(
                "severity_distribution", {}
            ),
            "tools_used": results.get("summary", {}).get("tools_used", []),
        }
