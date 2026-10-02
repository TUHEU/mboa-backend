import pytest
from fastapi.testclient import TestClient

from app.services.auth_service import GoogleIdentity


def test_register_login_and_current_user(client: TestClient):
    registration = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Yann Traveler",
            "email": "yann@example.com",
            "password": "SecurePass123!",
        },
    )
    assert registration.status_code == 201
    payload = registration.json()
    assert payload["token_type"] == "bearer"
    assert payload["user"]["role"] == "tourist"
    assert "password" not in payload["user"]

    login = client.post(
        "/api/v1/auth/login",
        json={"email": "yann@example.com", "password": "SecurePass123!"},
    )
    assert login.status_code == 200
    token = login.json()["access_token"]

    current_user = client.get(
        "/api/v1/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert current_user.status_code == 200
    assert current_user.json()["email"] == "yann@example.com"


def test_rejects_duplicate_email_and_invalid_password(client: TestClient):
    user = {
        "full_name": "Yann Traveler",
        "email": "yann@example.com",
        "password": "SecurePass123!",
    }
    assert client.post("/api/v1/auth/register", json=user).status_code == 201
    assert client.post("/api/v1/auth/register", json=user).status_code == 409

    response = client.post(
        "/api/v1/auth/login",
        json={"email": user["email"], "password": "WrongPassword1"},
    )
    assert response.status_code == 401


def test_rejects_weak_password(client: TestClient):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "full_name": "Yann Traveler",
            "email": "yann@example.com",
            "password": "password",
        },
    )
    assert response.status_code == 422


def test_google_login_creates_user_and_returns_nyetam_token(
    client: TestClient,
    monkeypatch: pytest.MonkeyPatch,
):
    monkeypatch.setattr(
        "app.routers.auth.verify_google_identity_token",
        lambda token, audience: GoogleIdentity(
            subject="google-subject-123",
            email="google.traveler@example.com",
            full_name="Google Traveler",
        ),
    )

    response = client.post(
        "/api/v1/auth/google",
        json={"id_token": "mock-google-identity-token"},
    )

    assert response.status_code == 200
    assert response.json()["access_token"]
    assert response.json()["user"]["email"] == "google.traveler@example.com"
    assert response.json()["user"]["role"] == "tourist"


def test_google_login_reports_missing_configuration(client: TestClient):
    response = client.post(
        "/api/v1/auth/google",
        json={"id_token": "unconfigured-google-token"},
    )

    assert response.status_code == 503
    assert response.json()["detail"] == "Google Sign-In is not configured."