from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root_ok():
    r = client.get("/")
    assert r.status_code == 200
    body = r.json()
    assert set(["service", "environment", "version", "docs"]).issubset(body.keys())


def test_health_ok():
    r = client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_tools_ok_jsonapi_shape():
    r = client.get("/api/v1/tools")
    assert r.status_code == 200

    payload = r.json()
    assert "data" in payload
    assert isinstance(payload["data"], list)
    assert len(payload["data"]) > 0

    first = payload["data"][0]
    assert first.get("type") == "tools"
    assert first.get("id") in {"nmap", "tshark", "ffuf"}
    assert "attributes" in first

    attrs = first["attributes"]
    assert attrs.get("name") == first.get("id")

    assert "variants" in attrs
    assert isinstance(attrs["variants"], list)