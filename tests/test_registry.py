"""Tests for the CloudOps AI application registry."""

import pytest

from kbass_monitoring.registry import (
    add_application,
    initialize_registry,
    list_applications,
)


@pytest.fixture
def isolated_registry(tmp_path, monkeypatch):
    """Use a separate temporary database for each test."""
    monkeypatch.setenv(
        "CLOUDOPS_DB_PATH",
        str(tmp_path / "applications.db"),
    )


def test_registry_starts_empty(isolated_registry):
    initialize_registry()
    assert list_applications() == []


def test_register_application(isolated_registry):
    application_id = add_application(
        name="Inventory API",
        environment="local",
        health_url="https://inventory.example.com/health",
        metrics_url="https://inventory.example.com/metrics",
    )

    applications = list_applications()

    assert application_id == 1
    assert len(applications) == 1
    assert applications[0]["name"] == "Inventory API"
    assert applications[0]["environment"] == "local"
    assert applications[0]["enabled"] == 1


def test_registry_persists_records(isolated_registry):
    add_application(
        name="AWS Backend",
        environment="aws",
        health_url="https://example.com/health",
    )

    initialize_registry()

    applications = list_applications()

    assert len(applications) == 1
    assert applications[0]["name"] == "AWS Backend"
    assert applications[0]["metrics_url"] is None


@pytest.mark.parametrize(
    "unsafe_url",
    [
        "http://localhost:8000/health",
        "http://127.0.0.1/health",
        "http://192.168.1.10/metrics",
        "http://169.254.169.254/latest/meta-data/",
        "ftp://example.com/file",
    ],
)
def test_registry_rejects_unsafe_urls(isolated_registry, unsafe_url):
    with pytest.raises(ValueError):
        add_application(
            name="Unsafe Application",
            environment="aws",
            health_url=unsafe_url,
        )

    assert list_applications() == []


def test_new_application_requires_monitoring_approval(isolated_registry):
    add_application(
        name="Inventory API",
        environment="aws",
        health_url="https://example.com/health",
        metrics_url="https://example.com/metrics",
    )

    assert list_applications()[0]["monitoring_approved"] == 0


def test_approve_and_revoke_monitoring(isolated_registry):
    from kbass_monitoring.registry import set_monitoring_approval

    application_id = add_application(
        name="Inventory API",
        environment="aws",
        health_url="https://example.com/health",
        metrics_url="https://example.com/metrics",
    )

    assert set_monitoring_approval(application_id, True) is True
    assert list_applications()[0]["monitoring_approved"] == 1

    assert set_monitoring_approval(application_id, False) is True
    assert list_applications()[0]["monitoring_approved"] == 0


def test_approval_rejects_unknown_application(isolated_registry):
    from kbass_monitoring.registry import set_monitoring_approval

    assert set_monitoring_approval(9999, True) is False


def test_approval_rejects_invalid_input(isolated_registry):
    from kbass_monitoring.registry import set_monitoring_approval

    with pytest.raises(ValueError):
        set_monitoring_approval("invalid", True)

    with pytest.raises(ValueError):
        set_monitoring_approval(1, "yes")


def test_new_application_requires_monitoring_approval(isolated_registry):
    add_application(
        name="Inventory API",
        environment="aws",
        health_url="https://example.com/health",
        metrics_url="https://example.com/metrics",
    )

    assert list_applications()[0]["monitoring_approved"] == 0


def test_approve_and_revoke_monitoring(isolated_registry):
    from kbass_monitoring.registry import set_monitoring_approval

    application_id = add_application(
        name="Inventory API",
        environment="aws",
        health_url="https://example.com/health",
        metrics_url="https://example.com/metrics",
    )

    assert set_monitoring_approval(application_id, True) is True
    assert list_applications()[0]["monitoring_approved"] == 1

    assert set_monitoring_approval(application_id, False) is True
    assert list_applications()[0]["monitoring_approved"] == 0


def test_approval_rejects_unknown_application(isolated_registry):
    from kbass_monitoring.registry import set_monitoring_approval

    assert set_monitoring_approval(9999, True) is False


def test_approval_rejects_invalid_input(isolated_registry):
    from kbass_monitoring.registry import set_monitoring_approval

    with pytest.raises(ValueError):
        set_monitoring_approval("invalid", True)

    with pytest.raises(ValueError):
        set_monitoring_approval(1, "yes")
