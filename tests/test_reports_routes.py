from fastapi.testclient import TestClient

from app.main import app
import app.api.v1.reports as reports_module
from app.core.database import get_db
from app.core.database import database
from datetime import datetime
import uuid


class FakeReportsService:
    async def get_reports(self):
        class Obj:
            id = uuid.uuid4()
            name = "report-1"
            description = "test report"
            results = {"summary": "ok"}
            created_at = datetime.utcnow()

        return [Obj()]


async def _override_db():
    yield None


def test_get_reports_ok(monkeypatch):
    monkeypatch.setattr(reports_module, "ReportsService", lambda db: FakeReportsService())
    app.dependency_overrides[get_db] = _override_db
    try:
        # Disable real DB side-effects from app lifespan
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        r = client.get("/api/v1/reports")
        assert r.status_code == 200
        body = r.json()
        assert isinstance(body.get("data"), list)
        first = body["data"][0]
        assert first.get("type") == "reports"
        assert first.get("attributes", {}).get("name") == "report-1"
        assert first.get("attributes", {}).get("results", {}).get("summary") == "ok"
    finally:
        app.dependency_overrides.clear()


def test_create_report_ok(monkeypatch):
    class FakeCreateService:
        async def create_report(self, report_create):
            class Obj:
                id = uuid.uuid4()
                name = report_create.name
                description = report_create.description
                results = {"summary": "ok"}
                created_at = datetime.utcnow()

            return Obj()

    monkeypatch.setattr(reports_module, "ReportsService", lambda db: FakeCreateService())
    app.dependency_overrides[get_db] = _override_db
    try:
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        payload = {
            "name": "report-x",
            "description": "desc",
            "jobs_ids": [str(uuid.uuid4())],
        }
        r = client.post("/api/v1/reports", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body.get("data", {}).get("type") == "reports"
        assert body["data"]["attributes"]["name"] == "report-x"
        assert body["data"]["attributes"]["results"]["summary"] == "ok"
    finally:
        app.dependency_overrides.clear()


def test_update_report_ok(monkeypatch):
    report_id = str(uuid.uuid4())

    class FakeUpdateService:
        async def update_report(self, _report_id, report_update):
            class Obj:
                id = uuid.UUID(report_id)
                name = report_update.name or "report-1"
                description = report_update.description or "desc"
                results = {"summary": "ok"}
                created_at = datetime.utcnow()

            return Obj()

    monkeypatch.setattr(reports_module, "ReportsService", lambda db: FakeUpdateService())
    app.dependency_overrides[get_db] = _override_db
    try:
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        payload = {"name": "report-updated"}
        r = client.patch(f"/api/v1/reports/{report_id}", json=payload)
        assert r.status_code == 200
        body = r.json()
        assert body.get("data", {}).get("type") == "reports"
        assert body["data"]["id"] == report_id
        assert body["data"]["attributes"]["name"] == "report-updated"
    finally:
        app.dependency_overrides.clear()


def test_create_report_invalid_payload(monkeypatch):
    class FakeService:
        async def create_report(self, report_create):
            raise AssertionError("Should not be called due to validation error")

    monkeypatch.setattr(reports_module, "ReportsService", lambda db: FakeService())
    app.dependency_overrides[get_db] = _override_db
    try:
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        # Missing required fields (name, jobs_ids)
        r = client.post("/api/v1/reports", json={"description": "desc"})
        assert r.status_code in (400, 422)
        assert "errors" in r.json()
    finally:
        app.dependency_overrides.clear()


def test_delete_report_ok_and_not_found(monkeypatch):
    report_id_ok = str(uuid.uuid4())
    report_id_missing = str(uuid.uuid4())

    class FakeDeleteService:
        async def delete_report(self, report_id: str):
            if report_id == report_id_missing:
                from app.core.exceptions import DeleteError

                raise DeleteError("not found")
            return None

    monkeypatch.setattr(reports_module, "ReportsService", lambda db: FakeDeleteService())
    app.dependency_overrides[get_db] = _override_db
    try:
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        # OK case
        r_ok = client.delete(f"/api/v1/reports/{report_id_ok}")
        assert r_ok.status_code == 200
        assert r_ok.json().get("data", {}).get("attributes", {}).get("message") == "Report deleted"

        # Not found case
        r_nf = client.delete(f"/api/v1/reports/{report_id_missing}")
        assert r_nf.status_code == 404
        assert "errors" in r_nf.json()
    finally:
        app.dependency_overrides.clear()


def test_reports_datetime_fields_are_iso(monkeypatch):
    class FakeReportsServiceISO:
        async def get_reports(self):
            class Obj:
                id = uuid.uuid4()
                name = "report-iso"
                description = "desc"
                results = {"summary": "ok"}
                created_at = datetime.utcnow()

            return [Obj()]

    monkeypatch.setattr(reports_module, "ReportsService", lambda db: FakeReportsServiceISO())
    app.dependency_overrides[get_db] = _override_db
    try:
        monkeypatch.setattr(database, "connect", lambda: None)
        monkeypatch.setattr(database, "create_tables", lambda: None)
        monkeypatch.setattr(database, "disconnect", lambda: None)

        client = TestClient(app)
        r = client.get("/api/v1/reports")
        assert r.status_code == 200
        attrs = r.json()["data"][0]["attributes"]
        assert isinstance(attrs["created_at"], str) and "T" in attrs["created_at"]
    finally:
        app.dependency_overrides.clear()


