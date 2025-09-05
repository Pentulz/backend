from pydantic import BaseModel


class AgentAuth(BaseModel):
    token: str
