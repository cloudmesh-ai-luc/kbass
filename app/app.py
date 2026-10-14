import json
import os
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, generate_latest

from troubleshooting import analyze_incident

app = Flask(__name__)

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
    return jsonify(
        {
            "application": "AI-Assisted Cloud Monitoring and Troubleshooting Dashboard",
            "status": "running",
            "message": "COMP 488 project application is running successfully.",
        }
    )


@app.route("/health")
def health():
    return jsonify(
        {
            "status": "healthy",
        }
    )


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, debug=True)