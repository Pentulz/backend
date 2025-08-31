import uuid
from datetime import timezone
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import CreateError, DeleteError, UpdateError
from app.models.agents import Agents
from app.models.jobs import Jobs
from app.schemas.agents import AgentCreate, AgentUpdate


class AgentsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_agents(self) -> List[Agents]:
        result = await self.db.execute(
            select(Agents).options(selectinload(Agents.jobs))
        )
        return result.scalars().all()

    async def get_agent_by_id(self, agent_id: str) -> Optional[Agents]:
        result = await self.db.execute(
            select(Agents)
            .options(selectinload(Agents.jobs))
            .where(Agents.id == agent_id)
        )
        return result.scalar_one_or_none()

    async def get_agent_by_hostname(self, hostname: str) -> Optional[Agents]:
        result = await self.db.execute(
            select(Agents).where(Agents.hostname == hostname)
        )
        return result.scalar_one_or_none()

    async def get_agent_by_name(self, name: str) -> Optional[Agents]:
        query = select(Agents).where(Agents.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_agent(self, agent: AgentCreate) -> Agents:
        if not agent.name:
            raise CreateError("Name is required")

        if await self.get_agent_by_name(agent.name):
            raise CreateError("Agent with this name already exists")

        # Generate token
        token = str(uuid.uuid4())

        # Create agent
        new_agent = Agents(
            name=agent.name,
            hostname=None,
            description=agent.description,
            platform=None,
            available_tools=[],
            token=token,
        )

        try:
            self.db.add(new_agent)
            await self.db.commit()
            return new_agent
        except IntegrityError as e:
            raise CreateError(f"Failed to create agent: {e}") from e

    async def get_jobs_by_agent_id(
        self, agent_id: str, completed: bool = False
    ) -> List[Jobs]:
        query = select(Jobs).where(Jobs.agent_id == agent_id)
        if completed:
            query = query.where(Jobs.completed_at.isnot(None))
        else:
            query = query.where(Jobs.completed_at.is_(None))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_agent(self, agent_id: str, agent_update: AgentUpdate) -> Agents:
        agent = await self.get_agent_by_id(agent_id)
        if not agent:
            raise UpdateError("Agent not found")

        if agent_update.hostname is not None:
            agent.hostname = agent_update.hostname
        if agent_update.description is not None:
            agent.description = agent_update.description
        if agent_update.platform is not None:
            agent.platform = agent_update.platform
        if agent_update.available_tools is not None:
            agent.available_tools = [
                tool.model_dump() for tool in agent_update.available_tools
            ]

        if agent_update.token is not None:
            agent.token = agent_update.token
        if agent_update.last_seen_at is not None:
            agent.last_seen_at = agent_update.last_seen_at.astimezone(
                timezone.utc
            ).replace(tzinfo=None)

        try:
            self.db.add(agent)
            await self.db.commit()
        except IntegrityError as e:
            raise UpdateError(f"Failed to update agent: {e}") from e

        return agent

    async def delete_agent(self, agent_id: str) -> None:
        agent = await self.get_agent_by_id(agent_id)
        if not agent:
            raise DeleteError("Agent not found")

        try:
            await self.db.delete(agent)
            await self.db.commit()
        except IntegrityError as e:
            raise DeleteError(f"Failed to delete agent: {e}") from e
