from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ResourceNotFound
from app.models.jobs import Jobs
from app.schemas.jobs import JobCreate, JobUpdate


class JobsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_jobs(self) -> List[Jobs]:
        query = select(Jobs)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_job_by_id(self, job_id: str) -> Optional[Jobs]:
        query = select(Jobs).where(Jobs.id == job_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_job(self, job: JobCreate) -> Jobs:
        new_job = Jobs(
            name=job.name,
            action=job.action,
            agent_id=job.agent_id,
            description=job.description,
        )

        self.db.add(new_job)
        await self.db.commit()

        return new_job

    async def update_job(self, job_id: str, job_update: JobUpdate) -> Jobs:
        job = await self.get_job_by_id(job_id)
        if not job:
            raise ResourceNotFound("Job not found")

        if job_update.name is not None:
            job.name = job_update.name
        if job_update.action is not None:
            job.action = job_update.action
        if job_update.agent_id is not None:
            job.agent_id = job_update.agent_id
        if job_update.description is not None:
            job.description = job_update.description
        if job_update.started_at is not None:
            job.started_at = job_update.started_at
        if job_update.completed_at is not None:
            job.completed_at = job_update.completed_at
        if job_update.results is not None:
            
            # TODO: Process results
            
            job.results = job_update.results

        self.db.add(job)
        await self.db.commit()

        return job

    async def delete_job(self, job_id: str) -> Jobs:
        job = await self.get_job_by_id(job_id)
        if not job:
            raise ResourceNotFound("Job not found")

        await self.db.delete(job)
        await self.db.commit()

        return job