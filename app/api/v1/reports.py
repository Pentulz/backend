from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.reponse import (
    create_error_response,
    create_success_response,
    create_success_response_list,
)
from app.schemas.reports import Report, ReportCreate
from app.services.reports_service import ReportsService
from app.utils.uuid import cast_uuid

router = APIRouter()


@router.get("/reports")
async def get_reports(db: AsyncSession = Depends(get_db)):
    """
    Get list of all reports
    """

    reports_service = ReportsService(db)
    reports = await reports_service.get_reports()

    response = [
        Report(
            id=report.id, results=report.results, created_at=report.created_at
        ).model_dump(mode="json")
        for report in reports
    ]

    return create_success_response_list("reports", response)


@router.post("/reports")
async def create_report(report: ReportCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new report
    """

    reports_service = ReportsService(db)
    report = await reports_service.create_report(report)

    return create_success_response(
        "reports", str(report.id), report.model_dump(mode="json")
    )


@router.get("/reports/{report_id}")
async def get_report(report_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get report by id
    """

    if not cast_uuid(report_id):
        return create_error_response("400", "Bad Request", "Invalid report id", 400)

    reports_service = ReportsService(db)
    report = await reports_service.get_report_by_id(report_id)

    if not report:
        return create_error_response("404", "Not Found", "Report not found", 404)

    response = Report(
        id=report.id, results=report.results, created_at=report.created_at
    )

    return create_success_response(
        "reports", str(report.id), response.model_dump(mode="json")
    )
