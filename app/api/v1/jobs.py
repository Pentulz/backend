from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.schemas.jobs import Job, JobCreate
from app.schemas.reponse import (
    create_error_response,
    create_success_response,
    create_success_response_list,
)
from app.services.jobs_service import JobsService
from app.utils.uuid import cast_uuid

router = APIRouter()


@router.get("/jobs")
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
        ).model_dump(mode="json")
        for job in jobs
    ]

    return create_success_response_list("jobs", response)


@router.post("/jobs")
async def create_job(job: JobCreate, db: AsyncSession = Depends(get_db)):
    """
    Create a new job
    """

    jobs_service = JobsService(db)
    job = await jobs_service.create_job(job)

    return create_success_response("jobs", str(job.id), job.model_dump(mode="json"))


@router.get("/jobs/{job_id}")
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
    )

    return response


@router.patch("/jobs/{job_id}")
async def update_job(job_id: str):
    """
    Update a job
    """

    return {"status": "ok"}
