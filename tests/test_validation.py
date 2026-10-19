"""Tests for CloudOps AI application registration validation."""

import pytest

from kbass_monitoring.validation import (
    validate_application,
    validate_endpoint_url,
)


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/health",
        "https://example.com/metrics",
        "http://example.com/health",
        "https://8.8.8.8/metrics",
    ],
)
def test_accepts_public_endpoints(url):
    validate_endpoint_url(url)


@pytest.mark.parametrize(
    "url",
    [
        "http://localhost:8000/health",
        "http://127.0.0.1/health",
        "http://192.168.1.10/metrics",
        "http://10.0.0.5/metrics",
        "http://169.254.169.254/latest/meta-data/",
        "http://service.internal/metrics",
        "http://service.local/health",
        "ftp://example.com/file",
        "https://user:password@example.com/metrics",
        "https://example.com:9090/metrics",
        "https://example.com/health#fragment",
    ],
)
def test_rejects_unsafe_endpoints(url):
    with pytest.raises(ValueError):
        validate_endpoint_url(url)


def test_valid_application():
    validate_application(
        name="Inventory API",
        environment="aws",
        health_url="https://example.com/health",
        metrics_url="https://example.com/metrics",
    )


def test_rejects_invalid_environment():
    with pytest.raises(ValueError):
        validate_application(
            name="Inventory API",
            environment="unknown",
            health_url="https://example.com/health",
        )


def test_rejects_empty_application_name():
    with pytest.raises(ValueError):
        validate_application(
            name="",
            environment="aws",
            health_url="https://example.com/health",
        )
