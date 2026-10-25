"""Tests for DNS safety checks before monitoring activation."""

import socket

import pytest


def test_public_dns_addresses_are_allowed(monkeypatch):
    from kbass_monitoring.validation import validate_public_dns

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443)),
        ],
    )

    assert validate_public_dns("example.com") is True


def test_private_dns_addresses_are_rejected(monkeypatch):
    from kbass_monitoring.validation import validate_public_dns

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("192.168.1.10", 443)),
        ],
    )

    with pytest.raises(ValueError):
        validate_public_dns("example.com")


def test_mixed_public_private_dns_is_rejected(monkeypatch):
    from kbass_monitoring.validation import validate_public_dns

    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("8.8.8.8", 443)),
            (socket.AF_INET, socket.SOCK_STREAM, 6, "", ("10.0.0.5", 443)),
        ],
    )

    with pytest.raises(ValueError):
        validate_public_dns("example.com")


def test_dns_resolution_failure_is_rejected(monkeypatch):
    from kbass_monitoring.validation import validate_public_dns

    def fail_resolution(*args, **kwargs):
        raise socket.gaierror("DNS resolution failed")

    monkeypatch.setattr(socket, "getaddrinfo", fail_resolution)

    with pytest.raises(ValueError):
        validate_public_dns("example.com")
