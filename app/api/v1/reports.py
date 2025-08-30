from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import CreateError, DeleteError, UpdateError
from app.core.response import (
    create_error_response,
    create_success_response,
    create_success_response_list,
)
from app.schemas.reports import (
    Report,
    ReportCreate,
    ReportResponse,
    ReportsListResponse,
    ReportUpdate,
)
from app.schemas.response_models import (
    DetailedBadRequestError,
    DetailedInternalServerError,
    DetailedNotFoundError,
    MessageResponse,
)
from app.services.reports import ReportsService
from app.utils.uuid import cast_uuid

router = APIRouter()


@router.get(
    "/reports",
    response_model=ReportsListResponse,
    responses={
        200: {"description": "List of reports retrieved successfully"},
        500: {
            "model": DetailedInternalServerError,
            "description": "Internal server error",
        },
    },
)
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


@router.post(
    "/reports",
    response_model=ReportResponse,
    responses={
        200: {"description": "Report created successfully"},
        400: {
            "model": DetailedBadRequestError,
            "description": "Bad request - invalid data",
        },
        500: {
            "model": DetailedInternalServerError,
            "description": "Internal server error",
        },
    },
)
async def create_report(report: ReportCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new report
    """

    try:
        reports_service = ReportsService(db)
        report = await reports_service.create_report(report)

        return create_success_response(
            "reports", str(report.id), report.model_dump(mode="json")
        )
    except CreateError as e:
        return create_error_response("400", "Bad Request", str(e), 400)


@router.get(
    "/reports/{report_id}",
    response_model=ReportResponse,
    responses={
        200: {"description": "Report retrieved successfully"},
        400: {
            "model": DetailedBadRequestError,
            "description": "Bad request - invalid report ID",
        },
        404: {"model": DetailedNotFoundError, "description": "Report not found"},
    },
)
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


@router.patch(
    "/reports/{report_id}",
    response_model=ReportResponse,
    responses={
        200: {"description": "Report updated successfully"},
        400: {
            "model": DetailedBadRequestError,
            "description": "Bad request - invalid report ID",
        },
        404: {"model": DetailedNotFoundError, "description": "Report not found"},
        500: {
            "model": DetailedInternalServerError,
            "description": "Internal server error",
        },
    },
)
async def update_report(
    report_id: str, report_update: ReportUpdate, db: AsyncSession = Depends(get_db)
):
    """
    Update report by id
    """

    if not cast_uuid(report_id):
        return create_error_response("400", "Bad Request", "Invalid report id", 400)

    try:
        reports_service = ReportsService(db)
        report = await reports_service.update_report(report_id, report_update)

        response = Report(
            id=report.id, results=report.results, created_at=report.created_at
        )

        return create_success_response(
            "reports", str(report.id), response.model_dump(mode="json")
        )
    except UpdateError:
        return create_error_response("404", "Not Found", "Report not found", 404)


@router.delete(
    "/reports/{report_id}",
    response_model=MessageResponse,
    responses={
        200: {"description": "Report deleted successfully"},
        400: {
            "model": DetailedBadRequestError,
            "description": "Bad request - invalid report ID",
        },
        404: {"model": DetailedNotFoundError, "description": "Report not found"},
    },
)
async def delete_report(report_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete report by id
    """

    if not cast_uuid(report_id):
        return create_error_response("400", "Bad Request", "Invalid report id", 400)

    try:
        reports_service = ReportsService(db)
        await reports_service.delete_report(report_id)

        return create_success_response(
            "reports", str(report_id), {"message": "Report deleted"}
        )
    except DeleteError:
        return create_error_response("404", "Not Found", "Report not found", 404)
