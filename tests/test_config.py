import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from app.core.config import Settings


def test_production_rejects_default_or_short_secret():
    with pytest.raises(ValidationError):
        Settings(environment="production")
    with pytest.raises(ValidationError):
        Settings(environment="production", secret_key="too-short")


def test_production_accepts_a_strong_secret():
    settings = Settings(environment="production", secret_key="x" * 48)
    assert settings.is_production


def test_development_allows_default_secret():
    assert not Settings().is_production


def _preflight(client: TestClient, origin: str):
    return client.options(
        "/api/v1/auth/login",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )


def test_cors_allows_flutter_web_on_any_localhost_port(client: TestClient):
    for origin in ("http://localhost:8123", "http://localhost:53211"):
        response = _preflight(client, origin)
        assert response.status_code == 200
        assert response.headers["access-control-allow-origin"] == origin


def test_cors_rejects_unknown_origins(client: TestClient):
    response = _preflight(client, "https://evil.example.com")
    assert "access-control-allow-origin" not in response.headers
