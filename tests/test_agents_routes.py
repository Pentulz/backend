from fastapi.testclient import TestClient

from app.main import app
import app.api.v1.agents as agents_module
from app.core.database import get_db
from app.core.database import database
from datetime import datetime
import uuid
from app.schemas.agents import PlatformType


class FakeAgentsService:
    async def get_agents(self):
        class Obj:
            id = uuid.uuid4()
            name = "agent-1"
            hostname = "host"
            description = "test agent"
            platform = PlatformType.LINUX
            available_tools = []
            token = "tok"
            last_seen_at = datetime.utcnow()
            created_at = datetime.utcnow()
            jobs = []

        return [Obj()]


async def _override_db():
    yield None


def test_get_agents_ok(monkeypatch):
    monkeypatch.setattr(agents_module, "AgentsService", lambda db: FakeAgentsService())
    app.dependency_overrides[get_db] = _override_db
    try:
        # Disable real DB side-effects from app lifespan
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        r = client.get("/api/v1/agents")
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body.get("data"), list)
        first = body["data"][0]
        assert first.get("type") == "agents"
        assert first.get("attributes", {}).get("name") == "agent-1"
    finally:
        app.dependency_overrides.clear()



def test_create_agent_ok(monkeypatch):
    class FakeCreateService:
        async def create_agent(self, agent_create):
            class Obj:
                id = uuid.uuid4()
                name = agent_create.name
                hostname = None
                description = agent_create.description
                platform = PlatformType.LINUX
                available_tools = []
                token = "tok"
                last_seen_at = datetime.utcnow()
                created_at = datetime.utcnow()

            return Obj()

    monkeypatch.setattr(agents_module, "AgentsService", lambda db: FakeCreateService())
    app.dependency_overrides[get_db] = _override_db
    try:
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        payload = {"name": "agent-x", "description": "desc"}
        r = client.post("/api/v1/agents", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body.get("data", {}).get("type") == "agents"
        assert body["data"]["attributes"]["hostname"] is None
        assert body["data"]["attributes"]["description"] == "desc"
    finally:
        app.dependency_overrides.clear()


def test_update_agent_ok(monkeypatch):
    agent_id = str(uuid.uuid4())

    class FakeUpdateService:
        async def update_agent(self, _agent_id, agent_update):
            class Obj:
                id = uuid.UUID(agent_id)
                name = agent_update.name or "agent-1"
                hostname = "host"
                description = agent_update.description or "test agent"
                platform = PlatformType.LINUX
                available_tools = []
                token = "tok"
                last_seen_at = datetime.utcnow()
                created_at = datetime.utcnow()

            return Obj()

    monkeypatch.setattr(agents_module, "AgentsService", lambda db: FakeUpdateService())
    app.dependency_overrides[get_db] = _override_db
    try:
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        payload = {"name": "agent-updated"}
        r = client.patch(f"/api/v1/agents/{agent_id}", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body.get("data", {}).get("type") == "agents"
        assert body["data"]["id"] == agent_id
        assert body["data"]["attributes"]["hostname"] == "host"
    finally:
        app.dependency_overrides.clear()


def test_create_agent_invalid_payload(monkeypatch):
    # Missing required field 'name'
    class FakeService:
        async def create_agent(self, agent_create):
            raise AssertionError("Should not be called due to validation error")

    monkeypatch.setattr(agents_module, "AgentsService", lambda db: FakeService())
    app.dependency_overrides[get_db] = _override_db
    try:
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        r = client.post("/api/v1/agents", json={"description": "desc"})
        assert r.status_code in (400, 422)
        body = r.json()
        assert "errors" in body
        assert isinstance(body["errors"], list)
    finally:
        app.dependency_overrides.clear()


def test_delete_agent_ok_and_not_found(monkeypatch):
    agent_id_ok = str(uuid.uuid4())
    agent_id_missing = str(uuid.uuid4())

    class FakeDeleteService:
        async def delete_agent(self, agent_id: str):
            if agent_id == agent_id_missing:
                from app.core.exceptions import DeleteError

                raise DeleteError("not found")
            return None

    monkeypatch.setattr(agents_module, "AgentsService", lambda db: FakeDeleteService())
    app.dependency_overrides[get_db] = _override_db
    try:
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        # OK case
        r_ok = client.delete(f"/api/v1/agents/{agent_id_ok}")
        assert r_ok.status_code == 200
        assert r_ok.json().get("data", {}).get("attributes", {}).get("message") == "Agent deleted"

        # Not found case
        r_nf = client.delete(f"/api/v1/agents/{agent_id_missing}")
        assert r_nf.status_code == 404
        assert "errors" in r_nf.json()
    finally:
        app.dependency_overrides.clear()


def test_agents_datetime_fields_are_iso(monkeypatch):
    class FakeAgentsServiceISO:
        async def get_agents(self):
            class Obj:
                id = uuid.uuid4()
                name = "agent-iso"
                hostname = "host"
                description = "desc"
                platform = PlatformType.LINUX
                available_tools = []
                token = "tok"
                last_seen_at = datetime.utcnow()
                created_at = datetime.utcnow()
                jobs = []

            return [Obj()]

    monkeypatch.setattr(agents_module, "AgentsService", lambda db: FakeAgentsServiceISO())
    app.dependency_overrides[get_db] = _override_db
    try:
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        r = client.get("/api/v1/agents")
        assert r.status_code == 200
        attrs = r.json()["data"][0]["attributes"]
        # Ensure ISO-like strings
        assert isinstance(attrs["created_at"], str) and "T" in attrs["created_at"]
        if attrs.get("last_seen_at") is not None:
            assert isinstance(attrs["last_seen_at"], str)
    finally:
        app.dependency_overrides.clear()

