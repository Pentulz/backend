import uuid
from datetime import datetime

from fastapi.testclient import TestClient

import app.api.v1.jobs as jobs_module
from app.core.database import database, get_db
from app.main import app


class FakeJobsService:
    async def get_jobs(self):
        class Obj:
            id = uuid.uuid4()
            name = "scan"
            # The API returns JobActionResponse with args list; internally service returns serialized dict
            action = {
                "cmd": "nmap",
                "variant": "tcp_connect_scan",
                "args": ["-sV", "example.com"],
            }
            agent_id = uuid.uuid4()
            description = None
            results = None
            started_at = None
            completed_at = None
            created_at = datetime.utcnow()
            success = None

        return [Obj()]


async def _override_db():
    yield None


def test_get_jobs_ok(monkeypatch):
    monkeypatch.setattr(jobs_module, "JobsService", lambda db: FakeJobsService())
    app.dependency_overrides[get_db] = _override_db
    try:
        # Disable real DB side-effects from app lifespan
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        r = client.get("/api/v1/jobs")
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body.get("data"), list)
        first = body["data"][0]
        assert first.get("type") == "jobs"
        assert first.get("attributes", {}).get("name") == "scan"
        assert first.get("attributes", {}).get("action", {}).get("cmd") == "nmap"
    finally:
        app.dependency_overrides.clear()


def test_create_job_ok(monkeypatch):
    class FakeCreateService:
        async def create_job(self, job_create):
            class Obj:
                id = uuid.uuid4()
                name = job_create.name
                action = {
                    "cmd": job_create.action.cmd,
                    "variant": job_create.action.variant,
                    "args": ["-sV", "example.com"],
                }
                agent_id = uuid.uuid4()
                description = job_create.description
                results = None
                started_at = None
                completed_at = None
                created_at = datetime.utcnow()
                success = None

            return Obj()

    monkeypatch.setattr(jobs_module, "JobsService", lambda db: FakeCreateService())
    app.dependency_overrides[get_db] = _override_db
    try:
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        payload = {
            "name": "scan",
            "description": "desc",
            "agent_id": str(uuid.uuid4()),
            "action": {
                "cmd": "nmap",
                "variant": "tcp_connect_scan",
                "args": {"target": "example.com"},
            },
        }
        r = client.post("/api/v1/jobs", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body.get("data", {}).get("type") == "jobs"
        assert body["data"]["attributes"]["action"]["cmd"] == "nmap"
    finally:
        app.dependency_overrides.clear()


def test_update_job_ok(monkeypatch):
    job_id = str(uuid.uuid4())

    class FakeUpdateService:
        async def update_job(self, _job_id, job_update):
            class Obj:
                id = uuid.UUID(job_id)
                name = job_update.name or "scan"
                action = {
                    "cmd": "nmap",
                    "variant": "tcp_connect_scan",
                    "args": ["-sV", "example.com"],
                }
                agent_id = uuid.uuid4()
                description = job_update.description or None
                results = None
                started_at = None
                completed_at = None
                created_at = datetime.utcnow()
                success = None

            return Obj()

    monkeypatch.setattr(jobs_module, "JobsService", lambda db: FakeUpdateService())
    app.dependency_overrides[get_db] = _override_db
    try:
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        payload = {"name": "scan-updated"}
        r = client.patch(f"/api/v1/jobs/{job_id}", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body.get("data", {}).get("type") == "jobs"
        assert body["data"]["id"] == job_id
        assert body["data"]["attributes"]["name"] == "scan-updated"
    finally:
        app.dependency_overrides.clear()


def test_create_job_invalid_payload(monkeypatch):
    class FakeService:
        async def create_job(self, job_create):
            raise AssertionError("Should not be called due to validation error")

    monkeypatch.setattr(jobs_module, "JobsService", lambda db: FakeService())
    app.dependency_overrides[get_db] = _override_db
    try:
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        # Missing required fields
        r = client.post("/api/v1/jobs", json={"name": "scan"})
        assert r.status_code in (400, 422)
        assert "errors" in r.json()
    finally:
        app.dependency_overrides.clear()


def test_delete_job_ok_and_not_found(monkeypatch):
    job_id_ok = str(uuid.uuid4())
    job_id_missing = str(uuid.uuid4())

    class FakeDeleteService:
        async def delete_job(self, job_id: str):
            if job_id == job_id_missing:
                from app.core.exceptions import DeleteError

                raise DeleteError("not found")
            return None

    monkeypatch.setattr(jobs_module, "JobsService", lambda db: FakeDeleteService())
    app.dependency_overrides[get_db] = _override_db
    try:
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        # OK case
        r_ok = client.delete(f"/api/v1/jobs/{job_id_ok}")
        assert r_ok.status_code == 200
        assert (
            r_ok.json().get("data", {}).get("attributes", {}).get("message")
            == "Job deleted"
        )

        # Not found case
        r_nf = client.delete(f"/api/v1/jobs/{job_id_missing}")
        assert r_nf.status_code == 404
        assert "errors" in r_nf.json()
    finally:
        app.dependency_overrides.clear()


def test_jobs_datetime_fields_are_iso(monkeypatch):
    class FakeJobsServiceISO:
        async def get_jobs(self):
            class Obj:
                id = uuid.uuid4()
                name = "scan-iso"
                action = {
                    "cmd": "nmap",
                    "variant": "tcp_connect_scan",
                    "args": ["-sV", "example.com"],
                }
                agent_id = uuid.uuid4()
                description = None
                results = None
                started_at = None
                completed_at = None
                created_at = datetime.utcnow()
                success = None

            return [Obj()]

    monkeypatch.setattr(jobs_module, "JobsService", lambda db: FakeJobsServiceISO())
    app.dependency_overrides[get_db] = _override_db
    try:
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        r = client.get("/api/v1/jobs")
        assert r.status_code == 200
        attrs = r.json()["data"][0]["attributes"]
        assert isinstance(attrs["created_at"], str) and "T" in attrs["created_at"]
        if attrs.get("started_at") is not None:
            assert isinstance(attrs["started_at"], str)
        if attrs.get("completed_at") is not None:
            assert isinstance(attrs["completed_at"], str)
    finally:
        app.dependency_overrides.clear()
