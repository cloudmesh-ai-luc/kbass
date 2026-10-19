"""Security tests for browser-based application registration."""

import pytest

from kbass_monitoring.app import app, limiter


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.setenv("CLOUDOPS_ADMIN_TOKEN", "test-admin-token")
    monkeypatch.setenv(
        "CLOUDOPS_DB_PATH", str(tmp_path / "applications.db")
    )
    monkeypatch.delenv("CLOUDOPS_HTTPS_ENABLED", raising=False)

    app.config.update(
        TESTING=True,
        SECRET_KEY="test-session-secret",
    )

    limiter.reset()
    return app.test_client()


def application_data():
    return {
        "name": "Test Inventory API",
        "environment": "aws",
        "health_url": "https://example.com/health",
        "metrics_url": "https://example.com/metrics",
    }


def login(client):
    response = client.post(
        "/api/auth/login",
        json={"token": "test-admin-token"},
    )
    assert response.status_code == 200
    return response.json["csrf_token"]


def test_browser_registration_success(client):
    csrf_token = login(client)

    response = client.post(
        "/api/applications",
        json=application_data(),
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 201

    applications = client.get("/api/applications").json["applications"]
    assert len(applications) == 1
    assert applications[0]["name"] == "Test Inventory API"


def test_registration_requires_authentication(client):
    response = client.post(
        "/api/applications",
        json=application_data(),
    )

    assert response.status_code == 401


def test_registration_rejects_invalid_csrf(client):
    login(client)

    response = client.post(
        "/api/applications",
        json=application_data(),
        headers={"X-CSRF-Token": "invalid-token"},
    )

    assert response.status_code == 403


def test_api_token_registration_still_works(client):
    response = client.post(
        "/api/applications",
        json=application_data(),
        headers={"X-CloudOps-Token": "test-admin-token"},
    )

    assert response.status_code == 201


def test_invalid_api_token_cannot_fall_back_to_session(client):
    csrf_token = login(client)

    response = client.post(
        "/api/applications",
        json=application_data(),
        headers={
            "X-CloudOps-Token": "incorrect-token",
            "X-CSRF-Token": csrf_token,
        },
    )

    assert response.status_code == 401
