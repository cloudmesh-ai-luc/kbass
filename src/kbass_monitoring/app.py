import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from flask import Flask, Response, jsonify, render_template, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

from .troubleshooting import analyze_incident
from .registry import add_application, list_applications
from .auth import require_management_token

app = Flask(__name__)

# Browser management sessions are disabled until a secret is configured.
app.config.update(
    SECRET_KEY=os.environ.get("CLOUDOPS_SESSION_SECRET"),
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get(
        "CLOUDOPS_HTTPS_ENABLED", ""
    ).lower() == "true",
    PERMANENT_SESSION_LIFETIME=1800,
)

limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[],
    storage_uri=os.environ.get(
        "CLOUDOPS_RATE_LIMIT_STORAGE_URI", "memory://"
    ),
)

PROMETHEUS_URL = os.environ.get("PROMETHEUS_URL", "http://prometheus:9090").rstrip("/")

REQUEST_COUNT = Counter(
    "app_http_requests_total",
    "Total number of HTTP requests received by the application",
    ["method", "endpoint", "status"],
)


@app.after_request
def record_request(response):
    REQUEST_COUNT.labels(
        method=request.method,
        endpoint=request.path,
        status=response.status_code,
    ).inc()
    return response



def fetch_prometheus_alerts():
    """Retrieve active and pending alerts from Prometheus."""
    url = f"{PROMETHEUS_URL}/api/v1/alerts"

    with urlopen(url, timeout=5) as response:
        payload = json.load(response)

    if payload.get("status") != "success":
        raise ValueError("Prometheus returned an unsuccessful response")

    data = payload.get("data")
    if not isinstance(data, dict):
        raise ValueError("Prometheus returned invalid alert data")

    alerts = data.get("alerts")
    if not isinstance(alerts, list):
        raise ValueError("Prometheus returned an invalid alerts list")

    return alerts



@app.route("/api/incidents", methods=["GET"])
def get_incidents():
    """Return normalized active and pending Prometheus alerts."""
    try:
        alerts = fetch_prometheus_alerts()
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        app.logger.warning("Unable to retrieve Prometheus alerts: %s", exc)
        return jsonify({
            "status": "unavailable",
            "error": "Prometheus alert data is currently unavailable",
        }), 503

    incidents = []

    for alert in alerts:
        labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})

        incident = {
            "name": labels.get("alertname", "UnknownAlert"),
            "severity": labels.get("severity", "unknown"),
            "state": alert.get("state", "unknown"),
            "summary": annotations.get("summary", ""),
            "description": annotations.get("description", ""),
            "active_at": alert.get("activeAt"),
            "value": alert.get("value"),
            "labels": labels,
        }

        incident["analysis"] = analyze_incident(incident)
        incidents.append(incident)

    return jsonify({
        "status": "success",
        "count": len(incidents),
        "incidents": incidents,
    })


@app.route("/")
def home():
    """Render the CloudOps AI monitoring dashboard."""
    return render_template("dashboard.html")



@app.route("/api/applications", methods=["GET"])
def get_applications():
    """Return registered applications without exposing endpoint URLs."""
    applications = list_applications()

    return jsonify({
        "status": "success",
        "count": len(applications),
        "applications": [
            {
                "id": application["id"],
                "name": application["name"],
                "environment": application["environment"],
                "enabled": bool(application["enabled"]),
            }
            for application in applications
        ],
    })



@app.route("/api/applications", methods=["POST"])
def register_application():
    """Register an application using administrator authentication."""
    if "X-CloudOps-Token" in request.headers:
        auth_error = require_management_token()
        if auth_error is not None:
            return auth_error
    else:
        from .auth import require_browser_session, require_csrf_token

        if (
            os.environ.get("CLOUDOPS_ADMIN_TOKEN")
            and not app.config.get("SECRET_KEY")
        ):
            return jsonify({"error": "Authentication required"}), 401

        auth_error = require_browser_session()
        if auth_error is not None:
            return auth_error

        csrf_error = require_csrf_token()
        if csrf_error is not None:
            return csrf_error

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    try:
        application_id = add_application(
            name=data.get("name"),
            environment=data.get("environment"),
            health_url=data.get("health_url"),
            metrics_url=data.get("metrics_url"),
        )
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify({
        "status": "created",
        "id": application_id,
    }), 201


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
        }
    )


@app.route("/test/error")
def simulate_error():
    """Generate a controlled HTTP 500 response for monitoring tests."""
    if (
        os.environ.get("ENABLE_ERROR_SIMULATION") != "true"
        or request.remote_addr not in ("127.0.0.1", "::1")
    ):
        return jsonify({"error": "Not found"}), 404

    return jsonify({"error": "Simulated server failure"}), 500


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)




@app.route("/api/auth/login", methods=["POST"])
@limiter.limit("5 per minute")
def browser_login():
    """Authenticate an administrator and establish a browser session."""
    import secrets

    from flask import session
    from .auth import browser_login_configured

    if not browser_login_configured():
        return jsonify({"error": "Browser login is not configured"}), 503

    if (
        os.environ.get("CLOUDOPS_HTTPS_ENABLED", "").lower() == "true"
        and not request.is_secure
    ):
        return jsonify({"error": "HTTPS is required for browser login"}), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "A JSON object is required"}), 400

    supplied_token = data.get("token")

    if not isinstance(supplied_token, str) or not secrets.compare_digest(
        supplied_token, os.environ["CLOUDOPS_ADMIN_TOKEN"]
    ):
        return jsonify({"error": "Invalid credentials"}), 401

    session.clear()
    session.permanent = True
    session["cloudops_admin"] = True
    session["cloudops_csrf_token"] = secrets.token_urlsafe(32)

    return jsonify({
        "status": "authenticated",
        "csrf_token": session["cloudops_csrf_token"],
    })


@app.route("/api/auth/logout", methods=["POST"])
def browser_logout():
    """End an authenticated administrator browser session."""
    from flask import session
    from .auth import require_browser_session, require_csrf_token

    auth_error = require_browser_session()
    if auth_error is not None:
        return auth_error

    csrf_error = require_csrf_token()
    if csrf_error is not None:
        return csrf_error

    session.clear()

    return jsonify({
        "status": "logged_out",
    })


@app.route("/api/auth/session", methods=["GET"])
def browser_session_status():
    """Return the authenticated browser session's CSRF token."""
    from flask import session
    from .auth import require_browser_session

    auth_error = require_browser_session()
    if auth_error is not None:
        return auth_error

    csrf_token = session.get("cloudops_csrf_token")

    if not isinstance(csrf_token, str) or not csrf_token:
        return jsonify({"error": "Invalid browser session"}), 401

    return jsonify({
        "status": "authenticated",
        "csrf_token": csrf_token,
    })



@app.route("/api/discovery/preview", methods=["GET"])
def get_discovery_preview():
    """Preview registered Prometheus targets without activating them."""
    if "X-CloudOps-Token" in request.headers:
        auth_error = require_management_token()
    else:
        from .auth import require_browser_session
        auth_error = require_browser_session()

    if auth_error is not None:
        return auth_error

    from .discovery import preview_registered_targets

    groups = preview_registered_targets()

    return jsonify({
        "status": "success",
        "count": len(groups),
        "target_groups": groups,
    })


@app.route(
    "/api/applications/<int:application_id>/monitoring-approval",
    methods=["PATCH"],
)
def update_monitoring_approval(application_id):
    """Approve or revoke monitoring without activating Prometheus targets."""
    if "X-CloudOps-Token" in request.headers:
        auth_error = require_management_token()
        if auth_error is not None:
            return auth_error
    else:
        from .auth import require_browser_session, require_csrf_token

        auth_error = require_browser_session()
        if auth_error is not None:
            return auth_error

        csrf_error = require_csrf_token()
        if csrf_error is not None:
            return csrf_error

    data = request.get_json(silent=True)

    if not isinstance(data, dict) or type(data.get("approved")) is not bool:
        return jsonify({"error": "A boolean approved field is required"}), 400

    from .registry import set_monitoring_approval

    updated = set_monitoring_approval(application_id, data["approved"])

    if not updated:
        return jsonify({"error": "Application not found"}), 404

    return jsonify({
        "status": "success",
        "application_id": application_id,
        "monitoring_approved": data["approved"],
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=False)
