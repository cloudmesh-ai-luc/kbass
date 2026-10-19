"""Tests for pre-activation monitoring target validation."""

import pytest

from kbass_monitoring.discovery import build_approved_target_groups


def make_application(approved=True):
    return {
        "id": 1,
        "name": "Inventory API",
        "environment": "aws",
        "enabled": 1,
        "monitoring_approved": int(approved),
        "metrics_url": "https://inventory.example.com/metrics",
    }


def test_approved_public_target_passes(monkeypatch):
    from kbass_monitoring.discovery import validate_activation_targets

    monkeypatch.setattr(
        "kbass_monitoring.validation.validate_public_dns",
        lambda hostname: True,
    )

    groups = validate_activation_targets([make_application()])

    assert groups == build_approved_target_groups([make_application()])


def test_private_dns_target_is_rejected(monkeypatch):
    from kbass_monitoring.discovery import validate_activation_targets

    def reject_private(hostname):
        raise ValueError("Non-public DNS address")

    monkeypatch.setattr(
        "kbass_monitoring.validation.validate_public_dns",
        reject_private,
    )

    with pytest.raises(ValueError):
        validate_activation_targets([make_application()])


def test_unapproved_target_does_not_trigger_dns_lookup(monkeypatch):
    from kbass_monitoring.discovery import validate_activation_targets

    def unexpected_lookup(hostname):
        raise AssertionError("Unapproved target was resolved")

    monkeypatch.setattr(
        "kbass_monitoring.validation.validate_public_dns",
        unexpected_lookup,
    )

    assert validate_activation_targets([make_application(False)]) == []
