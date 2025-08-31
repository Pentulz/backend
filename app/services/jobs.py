from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import CreateError, DeleteError, UpdateError
from app.models.jobs import Jobs
from app.schemas.jobs import JobCreate, JobUpdate
from app.services.agents import AgentsService
from app.services.tools.tool_manager import ToolManager


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

    async def _validate_job_creation(self, job: JobCreate) -> None:
        """Validate job creation data beyond Pydantic validation"""

        # Validate agent
        if not job.agent_id:
            raise CreateError("Agent ID is required")

        # Get agent and validate
        agents_service = AgentsService(self.db)
        agent = await agents_service.get_agent_by_id(str(job.agent_id))

        if not agent:
            raise CreateError("Agent not found")

        # Check if agent has available tools
        if not agent.available_tools:
            raise CreateError("Agent does not have any available tools")

        # Validate action using template system
        tool_manager = ToolManager()

        # Check if tool exists
        tool = tool_manager.get_tool(job.action.name)
        if not tool:
            raise CreateError(f"Tool '{job.action.name}' is not available")

        # Check if template exists
        template = tool_manager.get_tool_variant(job.action.name, job.action.variant)
        if not template:
            raise CreateError(
                f"Template '{job.action.variant}' not found for tool '{job.action.name}'"
            )

        # Validate that all required arguments are provided
        for arg_def in template["argument_definitions"]:
            if arg_def["required"] and arg_def["name"] not in job.action.args:
                if arg_def["default_value"] is None:
                    raise CreateError(
                        f"Required argument '{arg_def['name']}' missing for action '{job.action.name}'"
                    )

        # Build command to validate it
        command_args = tool_manager.build_command_from_variant(
            job.action.name, job.action.variant, job.action.args
        )
        if not command_args:
            raise CreateError(
                f"Failed to build command for action '{job.action.name}' with template '{job.action.variant}'"
            )

        # Store the complete command with export arguments
        job.action.args = command_args

    async def create_job(self, job: JobCreate) -> Jobs:
        """Create a new job with comprehensive validation"""

        # Validate job data
        await self._validate_job_creation(job)

        # Create new job
        new_job = Jobs(
            name=job.name,
            action=job.action.dict(),  # convert to dict for storage
            agent_id=job.agent_id,
            description=job.description,
        )

        try:
            self.db.add(new_job)
            await self.db.commit()
            await self.db.refresh(new_job)
        except IntegrityError as e:
            await self.db.rollback()
            raise CreateError(f"Failed to create job: {e}") from e

        return new_job

    async def update_job(self, job_id: str, job_update: JobUpdate) -> Jobs:
        job = await self.get_job_by_id(job_id)
        if not job:
            raise UpdateError("Job not found")

        # If job is completed or started, it cannot be updated
        if job.completed_at is not None or job.started_at is not None:
            raise UpdateError("Job is completed or started")

        # Validate action if it's being updated
        if job_update.action is not None:
            temp_job = JobCreate(
                name=job.name,
                action=job_update.action,
                agent_id=job.agent_id or job_update.agent_id,
                description=job.description,
            )
            await self._validate_job_creation(temp_job)

        # Update fields
        if job_update.name is not None:
            job.name = job_update.name
        if job_update.action is not None:
            job.action = job_update.action.dict()
        if job_update.agent_id is not None:
            job.agent_id = job_update.agent_id
        if job_update.description is not None:
            job.description = job_update.description
        if job_update.started_at is not None:
            job.started_at = job_update.started_at
        if job_update.completed_at is not None:
            job.completed_at = job_update.completed_at
        if job_update.results is not None:
            job.results = job_update.results

        try:
            self.db.add(job)
            await self.db.commit()
            await self.db.refresh(job)
        except IntegrityError as e:
            await self.db.rollback()
            raise UpdateError(f"Failed to update job: {e}") from e

        return job

    async def delete_job(self, job_id: str) -> None:
        job = await self.get_job_by_id(job_id)
        if not job:
            raise DeleteError("Job not found")

        try:
            await self.db.delete(job)
            await self.db.commit()
        except IntegrityError as e:
            await self.db.rollback()
            raise DeleteError(f"Failed to delete job: {e}") from e
