"""Tests for CloudOps AI management authentication."""

from flask import Flask

from kbass_monitoring.auth import require_management_token


def create_test_app():
    app = Flask(__name__)

    @app.route("/protected")
    def protected():
        error = require_management_token()
        if error is not None:
            return error
        return {"status": "authorized"}

    return app


def test_management_disabled_without_token(monkeypatch):
    monkeypatch.delenv("CLOUDOPS_ADMIN_TOKEN", raising=False)

    client = create_test_app().test_client()
    response = client.get("/protected")

    assert response.status_code == 503


def test_missing_token_is_rejected(monkeypatch):
    monkeypatch.setenv("CLOUDOPS_ADMIN_TOKEN", "test-secret")

    client = create_test_app().test_client()
    response = client.get("/protected")

    assert response.status_code == 401


def test_invalid_token_is_rejected(monkeypatch):
    monkeypatch.setenv("CLOUDOPS_ADMIN_TOKEN", "test-secret")

    client = create_test_app().test_client()
    response = client.get(
        "/protected",
        headers={"X-CloudOps-Token": "wrong-token"},
    )

    assert response.status_code == 401


def test_valid_token_is_accepted(monkeypatch):
    monkeypatch.setenv("CLOUDOPS_ADMIN_TOKEN", "test-secret")

    client = create_test_app().test_client()
    response = client.get(
        "/protected",
        headers={"X-CloudOps-Token": "test-secret"},
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "authorized"
