"""Tests for Prometheus target generation."""

from kbass_monitoring.discovery import build_target_groups


def make_application(
    application_id=1,
    name="Inventory API",
    environment="aws",
    enabled=1,
    metrics_url="https://inventory.example.com/metrics",
):
    return {
        "id": application_id,
        "name": name,
        "environment": environment,
        "enabled": enabled,
        "metrics_url": metrics_url,
    }


def test_valid_application_generates_target():
    groups = build_target_groups([make_application()])

    assert groups == [{
        "targets": ["inventory.example.com"],
        "labels": {
            "application_id": "1",
            "application_name": "Inventory API",
            "environment": "aws",
        },
    }]


def test_disabled_application_is_excluded():
    groups = build_target_groups([
        make_application(enabled=0)
    ])

    assert groups == []


def test_application_without_metrics_is_excluded():
    groups = build_target_groups([
        make_application(metrics_url=None)
    ])

    assert groups == []


def test_http_endpoint_is_excluded():
    groups = build_target_groups([
        make_application(metrics_url="http://inventory.example.com/metrics")
    ])

    assert groups == []


def test_custom_metrics_path_is_excluded():
    groups = build_target_groups([
        make_application(metrics_url="https://inventory.example.com/custom")
    ])

    assert groups == []


def test_multiple_applications():
    groups = build_target_groups([
        make_application(),
        make_application(
            application_id=2,
            name="Payment API",
            environment="chameleon",
            metrics_url="https://payments.example.com/metrics",
        ),
    ])

    assert len(groups) == 2
    assert groups[0]["labels"]["application_id"] == "1"
    assert groups[1]["labels"]["application_id"] == "2"


def test_unapproved_application_is_excluded_from_active_targets():
    from kbass_monitoring.discovery import build_approved_target_groups

    application = make_application()
    application["monitoring_approved"] = 0

    assert build_approved_target_groups([application]) == []


def test_approved_application_is_included_in_active_targets():
    from kbass_monitoring.discovery import build_approved_target_groups

    application = make_application()
    application["monitoring_approved"] = 1

    groups = build_approved_target_groups([application])

    assert len(groups) == 1
    assert groups[0]["targets"] == ["inventory.example.com"]


def test_disabled_approved_application_is_excluded():
    from kbass_monitoring.discovery import build_approved_target_groups

    application = make_application(enabled=0)
    application["monitoring_approved"] = 1

    assert build_approved_target_groups([application]) == []


def test_mixed_approval_only_includes_approved_application():
    from kbass_monitoring.discovery import build_approved_target_groups

    unapproved = make_application()
    unapproved["monitoring_approved"] = 0

    approved = make_application(
        application_id=2,
        name="Payment API",
        metrics_url="https://payments.example.com/metrics",
    )
    approved["monitoring_approved"] = 1

    groups = build_approved_target_groups([unapproved, approved])

    assert len(groups) == 1
    assert groups[0]["labels"]["application_id"] == "2"
