"""Tests for the authenticated Prometheus discovery preview API."""

import pytest

from kbass_monitoring.app import app
from kbass_monitoring.registry import add_application


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


def test_preview_requires_authentication(client):
    response = client.get("/api/discovery/preview")

    assert response.status_code == 401


def test_preview_rejects_invalid_management_token(client):
    response = client.get(
        "/api/discovery/preview",
        headers={"X-CloudOps-Token": "wrong-token"},
    )

    assert response.status_code == 401


def test_preview_starts_empty(client):
    response = client.get(
        "/api/discovery/preview",
        headers={"X-CloudOps-Token": "test-secret"},
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "success",
        "count": 0,
        "target_groups": [],
    }


def test_preview_returns_eligible_targets(client):
    application_id = add_application(
        name="Inventory API",
        environment="aws",
        health_url="https://example.com/health",
        metrics_url="https://example.com/metrics",
    )

    response = client.get(
        "/api/discovery/preview",
        headers={"X-CloudOps-Token": "test-secret"},
    )

    data = response.get_json()

    assert response.status_code == 200
    assert data["count"] == 1
    assert data["target_groups"] == [{
        "targets": ["example.com"],
        "labels": {
            "application_id": str(application_id),
            "application_name": "Inventory API",
            "environment": "aws",
        },
    }]


def test_preview_accepts_authenticated_browser_session(client):
    with client.session_transaction() as session:
        session["cloudops_admin"] = True

    response = client.get("/api/discovery/preview")

    assert response.status_code == 200
    assert response.get_json()["status"] == "success"


def test_preview_does_not_write_target_file(client, tmp_path, monkeypatch):
    target_file = tmp_path / "registered-apps.json"
    target_file.write_text("[]")

    monkeypatch.chdir(tmp_path)

    add_application(
        name="Inventory API",
        environment="aws",
        health_url="https://example.com/health",
        metrics_url="https://example.com/metrics",
    )

    response = client.get(
        "/api/discovery/preview",
        headers={"X-CloudOps-Token": "test-secret"},
    )

    assert response.status_code == 200
    assert target_file.read_text() == "[]"
