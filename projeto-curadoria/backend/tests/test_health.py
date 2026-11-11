from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import app

client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "app" in body and "environment" in body


def test_health_does_not_expose_secrets():
    body = client.get("/api/health").json()
    for forbidden in ("secret_key", "llm_api_key", "youtube_api_key", "database_url"):
        assert forbidden not in body


def test_cors_origins_parsing():
    s = Settings(cors_origins="http://a.com, http://b.com ,")
    assert s.cors_origins_list == ["http://a.com", "http://b.com"]


def test_secrets_not_in_repr():
    s = Settings(secret_key="abc123", llm_api_key="sk-xyz", youtube_api_key="yt-key")
    text = repr(s)
    assert "abc123" not in text
    assert "sk-xyz" not in text
    assert "yt-key" not in text
