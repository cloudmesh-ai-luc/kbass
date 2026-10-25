"""Tests for the CloudOps AI browser logout endpoint."""

import pytest

from kbass_monitoring.app import app, limiter


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CLOUDOPS_ADMIN_TOKEN", "test-admin-token")
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-session-secret",
    )
    limiter.reset()
    return app.test_client()


def login(client):
    response = client.post(
        "/api/auth/login",
        json={"token": "test-admin-token"},
    )
    assert response.status_code == 200
    return response.json["csrf_token"]


def test_logout_success(client):
    csrf_token = login(client)

    response = client.post(
        "/api/auth/logout",
        headers={"X-CSRF-Token": csrf_token},
    )

    assert response.status_code == 200
    assert response.json["status"] == "logged_out"

    with client.session_transaction() as session:
        assert session.get("cloudops_admin") is None
        assert session.get("cloudops_csrf_token") is None


def test_logout_requires_authentication(client):
    response = client.post("/api/auth/logout")

    assert response.status_code == 401


def test_logout_rejects_invalid_csrf(client):
    login(client)

    response = client.post(
        "/api/auth/logout",
        headers={"X-CSRF-Token": "invalid-token"},
    )

    assert response.status_code == 403

    with client.session_transaction() as session:
        assert session.get("cloudops_admin") is True
