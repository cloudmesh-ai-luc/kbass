"""Tests for administrator-controlled monitoring approval."""

import pytest

from kbass_monitoring.app import app
from kbass_monitoring.registry import add_application, list_applications


@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setenv(
        "CLOUDOPS_DB_PATH",
        str(tmp_path / "applications.db"),
    )
    monkeypatch.setenv("CLOUDOPS_ADMIN_TOKEN", "test-secret")
    monkeypatch.setenv("CLOUDOPS_SESSION_SECRET", "test-session-secret")
    app.config.update(TESTING=True, SECRET_KEY="test-session-secret")

    with app.test_client() as test_client:
        yield test_client


def create_application():
    return add_application(
        name="Inventory API",
        environment="aws",
        health_url="https://example.com/health",
        metrics_url="https://example.com/metrics",
    )


def approval_url(application_id):
    return f"/api/applications/{application_id}/monitoring-approval"


def test_approval_requires_authentication(client):
    application_id = create_application()

    response = client.patch(
        approval_url(application_id),
        json={"approved": True},
    )

    assert response.status_code == 401
    assert list_applications()[0]["monitoring_approved"] == 0


def test_approval_rejects_invalid_token(client):
    application_id = create_application()

    response = client.patch(
        approval_url(application_id),
        headers={"X-CloudOps-Token": "wrong-token"},
        json={"approved": True},
    )

    assert response.status_code == 401


def test_admin_can_approve_monitoring(client):
    application_id = create_application()

    response = client.patch(
        approval_url(application_id),
        headers={"X-CloudOps-Token": "test-secret"},
        json={"approved": True},
    )

    assert response.status_code == 200
    assert response.get_json()["monitoring_approved"] is True
    assert list_applications()[0]["monitoring_approved"] == 1


def test_admin_can_revoke_monitoring(client):
    application_id = create_application()

    client.patch(
        approval_url(application_id),
        headers={"X-CloudOps-Token": "test-secret"},
        json={"approved": True},
    )

    response = client.patch(
        approval_url(application_id),
        headers={"X-CloudOps-Token": "test-secret"},
        json={"approved": False},
    )

    assert response.status_code == 200
    assert list_applications()[0]["monitoring_approved"] == 0


def test_approval_rejects_unknown_application(client):
    response = client.patch(
        approval_url(9999),
        headers={"X-CloudOps-Token": "test-secret"},
        json={"approved": True},
    )

    assert response.status_code == 404


def test_approval_requires_boolean(client):
    application_id = create_application()

    response = client.patch(
        approval_url(application_id),
        headers={"X-CloudOps-Token": "test-secret"},
        json={"approved": "yes"},
    )

    assert response.status_code == 400
    assert list_applications()[0]["monitoring_approved"] == 0


def test_browser_approval_requires_csrf(client):
    application_id = create_application()

    with client.session_transaction() as session:
        session["cloudops_admin"] = True
        session["cloudops_csrf_token"] = "test-csrf"

    response = client.patch(
        approval_url(application_id),
        json={"approved": True},
    )

    assert response.status_code == 403
    assert list_applications()[0]["monitoring_approved"] == 0


def test_browser_admin_can_approve_with_csrf(client):
    application_id = create_application()

    with client.session_transaction() as session:
        session["cloudops_admin"] = True
        session["cloudops_csrf_token"] = "test-csrf"

    response = client.patch(
        approval_url(application_id),
        headers={"X-CSRF-Token": "test-csrf"},
        json={"approved": True},
    )

    assert response.status_code == 200
    assert list_applications()[0]["monitoring_approved"] == 1
