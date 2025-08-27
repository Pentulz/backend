import uuid
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.agents import Agents
from app.schemas.agents import AgentCreate


class AgentsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_agents(self) -> List[Agents]:
        query = select(Agents)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_agent_by_id(self, agent_id: str) -> Optional[Agents]:
        query = select(Agents).where(Agents.id == agent_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_agent(self, agent: AgentCreate) -> Agents:
        # Generate token
        token = str(uuid.uuid4())

        # Create agent
        new_agent = Agents(
            hostname=agent.hostname,
            description=agent.description,
            platform=None,
            available_tools={},
            token=token,
        )

        self.db.add(new_agent)
        await self.db.commit()

        return new_agent
