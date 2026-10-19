"""Tests for the CloudOps AI browser login endpoint."""

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


def test_login_success(client):
    response = client.post(
        "/api/auth/login",
        json={"token": "test-admin-token"},
    )

    assert response.status_code == 200
    assert response.json["status"] == "authenticated"
    assert response.json["csrf_token"]

    with client.session_transaction() as session:
        assert session["cloudops_admin"] is True
        assert session["cloudops_csrf_token"] == response.json["csrf_token"]
        assert session.permanent is True


def test_login_rejects_invalid_credentials(client):
    response = client.post(
        "/api/auth/login",
        json={"token": "incorrect-token"},
    )

    assert response.status_code == 401

    with client.session_transaction() as session:
        assert session.get("cloudops_admin") is not True


def test_login_requires_configuration(client, monkeypatch):
    monkeypatch.delenv("CLOUDOPS_ADMIN_TOKEN")

    response = client.post(
        "/api/auth/login",
        json={"token": "test-admin-token"},
    )

    assert response.status_code == 503


def test_login_rejects_invalid_json(client):
    response = client.post(
        "/api/auth/login",
        data="not-json",
        content_type="application/json",
    )

    assert response.status_code == 400
