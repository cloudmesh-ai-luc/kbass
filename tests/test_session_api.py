"""Tests for the CloudOps AI browser session endpoint."""

import pytest

from kbass_monitoring.app import app, limiter


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CLOUDOPS_ADMIN_TOKEN", "test-admin-token")
    monkeypatch.delenv("CLOUDOPS_HTTPS_ENABLED", raising=False)

    app.config.update(
        TESTING=True,
        SECRET_KEY="test-session-secret",
    )

    limiter.reset()
    return app.test_client()


def test_session_requires_authentication(client):
    response = client.get("/api/auth/session")
    assert response.status_code == 401


def test_session_restoration(client):
    login = client.post(
        "/api/auth/login",
        json={"token": "test-admin-token"},
    )

    assert login.status_code == 200

    response = client.get("/api/auth/session")

    assert response.status_code == 200
    assert response.json["status"] == "authenticated"
    assert response.json["csrf_token"] == login.json["csrf_token"]


def test_session_rejected_after_logout(client):
    login = client.post(
        "/api/auth/login",
        json={"token": "test-admin-token"},
    )

    csrf_token = login.json["csrf_token"]

    logout = client.post(
        "/api/auth/logout",
        headers={"X-CSRF-Token": csrf_token},
    )

    assert logout.status_code == 200
    assert client.get("/api/auth/session").status_code == 401


def test_session_requires_https_when_enabled(client, monkeypatch):
    login = client.post(
        "/api/auth/login",
        json={"token": "test-admin-token"},
    )

    assert login.status_code == 200

    monkeypatch.setenv("CLOUDOPS_HTTPS_ENABLED", "true")

    response = client.get("/api/auth/session")
    assert response.status_code == 403
