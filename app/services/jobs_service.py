from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.jobs import Jobs
from app.schemas.jobs import JobCreate


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
