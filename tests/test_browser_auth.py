"""Tests for CloudOps AI browser authentication helpers."""

import pytest
from flask import session

from kbass_monitoring.app import app
from kbass_monitoring.auth import (
    browser_login_configured,
    require_browser_session,
    require_csrf_token,
)


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("CLOUDOPS_ADMIN_TOKEN", "test-admin-token")
    app.config.update(
        TESTING=True,
        SECRET_KEY="test-session-secret",
    )
    return app.test_client()


def test_browser_login_requires_configuration(client, monkeypatch):
    monkeypatch.delenv("CLOUDOPS_ADMIN_TOKEN")
    with app.test_request_context():
        assert browser_login_configured() is False
        response, status = require_browser_session()
        assert status == 503


def test_browser_session_rejects_unauthenticated_user(client):
    with app.test_request_context():
        response, status = require_browser_session()
        assert status == 401


def test_browser_session_accepts_authenticated_user(client):
    with app.test_request_context():
        session["cloudops_admin"] = True
        assert require_browser_session() is None


def test_csrf_token_validation(client):
    with app.test_request_context(headers={"X-CSRF-Token": "correct-token"}):
        session["cloudops_csrf_token"] = "correct-token"
        assert require_csrf_token() is None

    with app.test_request_context(headers={"X-CSRF-Token": "wrong-token"}):
        session["cloudops_csrf_token"] = "correct-token"
        response, status = require_csrf_token()
        assert status == 403
