"""Tests for the CloudOps AI application API."""

import pytest

from kbass_monitoring.app import app
from kbass_monitoring.registry import add_application


@pytest.fixture
def client(tmp_path, monkeypatch):
    """Use an isolated database for each API test."""
    monkeypatch.setenv(
        "CLOUDOPS_DB_PATH",
        str(tmp_path / "applications.db"),
    )
    app.config["TESTING"] = True

    with app.test_client() as test_client:
        yield test_client


def test_applications_api_starts_empty(client):
    response = client.get("/api/applications")

    assert response.status_code == 200
    assert response.get_json() == {
        "status": "success",
        "count": 0,
        "applications": [],
    }


def test_applications_api_lists_registered_apps(client):
    add_application(
        name="Inventory API",
        environment="aws",
        health_url="https://example.com/health",
        metrics_url="https://example.com/metrics",
    )

    response = client.get("/api/applications")
    data = response.get_json()

    assert response.status_code == 200
    assert data["count"] == 1
    assert data["applications"][0]["name"] == "Inventory API"
    assert data["applications"][0]["environment"] == "aws"
    assert data["applications"][0]["enabled"] is True


def test_applications_api_does_not_expose_urls(client):
    add_application(
        name="Secure API",
        environment="chameleon",
        health_url="https://example.com/health",
        metrics_url="https://example.com/metrics",
    )

    response = client.get("/api/applications")
    application = response.get_json()["applications"][0]

    assert "health_url" not in application
    assert "metrics_url" not in application


def test_applications_api_rejects_post(client, monkeypatch):
    monkeypatch.setenv("CLOUDOPS_ADMIN_TOKEN", "test-secret")

    response = client.post(
        "/api/applications",
        json={"name": "Unauthorized Application"},
    )

    assert response.status_code == 401


def test_authenticated_registration(client, monkeypatch):
    monkeypatch.setenv("CLOUDOPS_ADMIN_TOKEN", "test-secret")

    response = client.post(
        "/api/applications",
        headers={"X-CloudOps-Token": "test-secret"},
        json={
            "name": "Inventory API",
            "environment": "aws",
            "health_url": "https://example.com/health",
            "metrics_url": "https://example.com/metrics",
        },
    )

    assert response.status_code == 201
    assert response.get_json()["status"] == "created"

    applications = client.get("/api/applications").get_json()
    assert applications["count"] == 1
    assert applications["applications"][0]["name"] == "Inventory API"


def test_registration_rejects_unsafe_url(client, monkeypatch):
    monkeypatch.setenv("CLOUDOPS_ADMIN_TOKEN", "test-secret")

    response = client.post(
        "/api/applications",
        headers={"X-CloudOps-Token": "test-secret"},
        json={
            "name": "Unsafe Application",
            "environment": "aws",
            "health_url": "http://127.0.0.1/health",
        },
    )

    assert response.status_code == 400
    assert client.get("/api/applications").get_json()["count"] == 0


def test_registration_disabled_without_admin_token(client, monkeypatch):
    monkeypatch.delenv("CLOUDOPS_ADMIN_TOKEN", raising=False)

    response = client.post(
        "/api/applications",
        json={
            "name": "Inventory API",
            "environment": "aws",
            "health_url": "https://example.com/health",
        },
    )

    assert response.status_code == 503


def test_registration_requires_json_object(client, monkeypatch):
    monkeypatch.setenv("CLOUDOPS_ADMIN_TOKEN", "test-secret")

    response = client.post(
        "/api/applications",
        headers={"X-CloudOps-Token": "test-secret"},
        json=["invalid", "payload"],
    )

    assert response.status_code == 400
