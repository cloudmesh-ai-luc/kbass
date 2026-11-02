"""Tests for the CloudOps AI Prometheus metrics endpoint."""

from kbass_monitoring.app import app


def test_metrics_endpoint_returns_prometheus_metrics():
    app.config["TESTING"] = True

    with app.test_client() as client:
        response = client.get("/health")
        assert response.status_code == 200

        response = client.get("/metrics")

    assert response.status_code == 200
    assert response.mimetype == "text/plain"

    metrics = response.get_data(as_text=True)

    assert "app_http_requests_total" in metrics
    assert 'method="GET"' in metrics
    assert 'endpoint="/health"' in metrics
    assert 'status="200"' in metrics
