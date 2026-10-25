"""Authentication helpers for CloudOps AI management APIs."""

import os
import secrets

from flask import jsonify, request


def require_management_token():
    """Return an error response unless a valid management token is supplied."""
    configured_token = os.environ.get("CLOUDOPS_ADMIN_TOKEN")

    if not configured_token:
        return jsonify({
            "error": "Application management is not configured"
        }), 503

    supplied_token = request.headers.get("X-CloudOps-Token", "")

    if not secrets.compare_digest(supplied_token, configured_token):
        return jsonify({
            "error": "Unauthorized"
        }), 401

    return None


def browser_login_configured():
    """Check whether browser authentication can be enabled."""
    from flask import current_app

    return bool(
        current_app.config.get("SECRET_KEY")
        and os.environ.get("CLOUDOPS_ADMIN_TOKEN")
    )


def require_browser_session():
    """Require an authenticated administrator browser session."""
    from flask import session

    if not browser_login_configured():
        return jsonify({"error": "Browser login is not configured"}), 503

    if (
        os.environ.get("CLOUDOPS_HTTPS_ENABLED", "").lower() == "true"
        and not request.is_secure
    ):
        return jsonify({"error": "HTTPS is required"}), 403

    if session.get("cloudops_admin") is not True:
        return jsonify({"error": "Authentication required"}), 401

    return None


def require_csrf_token():
    """Validate the CSRF token for a browser management request."""
    from flask import session

    expected = session.get("cloudops_csrf_token")
    supplied = request.headers.get("X-CSRF-Token", "")

    if (
        not isinstance(expected, str)
        or not expected
        or not secrets.compare_digest(supplied, expected)
    ):
        return jsonify({"error": "Invalid CSRF token"}), 403

    return None
