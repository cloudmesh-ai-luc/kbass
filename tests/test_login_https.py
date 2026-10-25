"""Tests for HTTPS enforcement on browser login."""

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


def test_http_login_rejected_when_https_required(client, monkeypatch):
    monkeypatch.setenv("CLOUDOPS_HTTPS_ENABLED", "true")

    response = client.post(
        "/api/auth/login",
        json={"token": "test-admin-token"},
    )

    assert response.status_code == 403
    assert response.json["error"] == "HTTPS is required for browser login"


def test_https_login_allowed_when_required(client, monkeypatch):
    monkeypatch.setenv("CLOUDOPS_HTTPS_ENABLED", "true")

    response = client.post(
        "/api/auth/login",
        json={"token": "test-admin-token"},
        environ_overrides={"wsgi.url_scheme": "https"},
    )

    assert response.status_code == 200
    assert response.json["status"] == "authenticated"


def test_http_login_allowed_in_local_development(client):
    response = client.post(
        "/api/auth/login",
        json={"token": "test-admin-token"},
    )

    assert response.status_code == 200
    assert response.json["status"] == "authenticated"
