from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.exceptions import CreateError, DeleteError, UpdateError
from app.core.response import (
    create_error_response,
    create_success_response,
    create_success_response_list,
)
from app.schemas.jobs import Job, JobCreate, JobResponse, JobsListResponse, JobUpdate
from app.schemas.response_models import (
    DetailedBadRequestError,
    DetailedInternalServerError,
    DetailedNotFoundError,
    MessageResponse,
)
from app.services.jobs import JobsService
from app.utils.uuid import cast_uuid

router = APIRouter()


@router.get(
    "/jobs",
    response_model=JobsListResponse,
    responses={
        200: {"description": "List of jobs retrieved successfully"},
        500: {
            "model": DetailedInternalServerError,
            "description": "Internal server error",
        },
    },
)
async def get_jobs(db: AsyncSession = Depends(get_db)):
    """
    Get list of all jobs
    """

    jobs_service = JobsService(db)
    jobs = await jobs_service.get_jobs()

    response = [
        Job(
            id=job.id,
            name=job.name,
            action=job.action,
            agent_id=job.agent_id,
            description=job.description,
            results=job.results,
            started_at=job.started_at,
            completed_at=job.completed_at,
            created_at=job.created_at,
            success=job.success,
        ).model_dump(mode="json")
        for job in jobs
    ]

    return create_success_response_list("jobs", response)


@router.post(
    "/jobs",
    response_model=JobResponse,
    responses={
        200: {"description": "Job created successfully"},
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
async def create_job(job: JobCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new job
    """

    try:
        jobs_service = JobsService(db)
        job = await jobs_service.create_job(job)

        response = Job(
            id=job.id,
            name=job.name,
            action=job.action,
            agent_id=job.agent_id,
            description=job.description,
            results=job.results,
            started_at=job.started_at,
            completed_at=job.completed_at,
            created_at=job.created_at,
        )

        return create_success_response(
            "jobs", str(job.id), response.model_dump(mode="json")
        )
    except CreateError as e:
        return create_error_response("400", "Bad Request", str(e), 400)


@router.get(
    "/jobs/{job_id}",
    response_model=JobResponse,
    responses={
        200: {"description": "Job retrieved successfully"},
        400: {
            "model": DetailedBadRequestError,
            "description": "Bad request - invalid job ID",
        },
        404: {"model": DetailedNotFoundError, "description": "Job not found"},
    },
)
async def get_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """
    Get job by id
    """

    if not cast_uuid(job_id):
        return create_error_response("400", "Bad Request", "Invalid job id", 400)

    jobs_service = JobsService(db)
    job = await jobs_service.get_job_by_id(job_id)

    if not job:
        return create_error_response("404", "Not Found", "Job not found", 404)

    response = Job(
        id=job.id,
        name=job.name,
        action=job.action,
        agent_id=job.agent_id,
        description=job.description,
        results=job.results,
        started_at=job.started_at,
        completed_at=job.completed_at,
        created_at=job.created_at,
        success=job.success,
    )

    return create_success_response(
        "jobs", str(job.id), response.model_dump(mode="json")
    )


@router.delete(
    "/jobs/{job_id}",
    response_model=MessageResponse,
    responses={
        200: {"description": "Job deleted successfully"},
        400: {
            "model": DetailedBadRequestError,
            "description": "Bad request - invalid job ID",
        },
        404: {"model": DetailedNotFoundError, "description": "Job not found"},
    },
)
async def delete_job(job_id: str, db: AsyncSession = Depends(get_db)):
    """
    Delete a job
    """
    if not cast_uuid(job_id):
        return create_error_response("400", "Bad Request", "Invalid job id", 400)

    try:
        jobs_service = JobsService(db)
        await jobs_service.delete_job(job_id)
        return create_success_response("jobs", str(job_id), {"message": "Job deleted"})
    except DeleteError:
        return create_error_response("404", "Not Found", "Job not found", 404)


@router.patch(
    "/jobs/{job_id}",
    response_model=JobResponse,
    responses={
        200: {"description": "Job updated successfully"},
        400: {
            "model": DetailedBadRequestError,
            "description": "Bad request - invalid data",
        },
        404: {"model": DetailedNotFoundError, "description": "Job not found"},
        500: {
            "model": DetailedInternalServerError,
            "description": "Internal server error",
        },
    },
)
async def update_job(job_id: str, job: JobUpdate, db: AsyncSession = Depends(get_db)):
    """
    Update a job
    """

    if not cast_uuid(job_id):
        print("Invalid job id")
        return create_error_response("400", "Bad Request", "Invalid job id", 400)

    try:
        jobs_service = JobsService(db)
        job = await jobs_service.update_job(job_id, job)

        response = Job(
            id=job.id,
            name=job.name,
            action=job.action,
            agent_id=job.agent_id,  
            description=job.description,
            results=job.results,
            started_at=job.started_at,
            completed_at=job.completed_at,
            created_at=job.created_at,
            success=job.success,
        )

        return create_success_response(
            "jobs", str(job.id), response.model_dump(mode="json")
        )
    except UpdateError:
        return create_error_response("404", "Not Found", "Job not found", 404)
