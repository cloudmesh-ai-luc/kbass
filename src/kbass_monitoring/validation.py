"""Input validation for CloudOps AI application registration."""

import ipaddress
from urllib.parse import urlsplit


ALLOWED_ENVIRONMENTS = {"local", "chameleon", "aws", "other"}


def validate_application(name, environment, health_url, metrics_url=None):
    """Validate registration fields without making network requests."""
    if not isinstance(name, str) or not 1 <= len(name.strip()) <= 100:
        raise ValueError("Application name must contain 1–100 characters")

    if environment not in ALLOWED_ENVIRONMENTS:
        raise ValueError("Invalid application environment")

    validate_endpoint_url(health_url)

    if metrics_url is not None:
        validate_endpoint_url(metrics_url)


def validate_endpoint_url(url):
    """Apply initial URL restrictions to monitoring endpoints."""
    if not isinstance(url, str) or not url or len(url) > 2048:
        raise ValueError("Invalid endpoint URL")

    try:
        parsed = urlsplit(url)
        port = parsed.port
        hostname = parsed.hostname
    except ValueError as exc:
        raise ValueError("Malformed endpoint URL") from exc

    if parsed.scheme not in {"http", "https"}:
        raise ValueError("Only HTTP and HTTPS endpoints are supported")

    if not hostname or parsed.username or parsed.password:
        raise ValueError("Endpoint hostname or credentials are invalid")

    if port not in {None, 80, 443}:
        raise ValueError("Only standard HTTP/HTTPS ports are permitted")

    if parsed.fragment:
        raise ValueError("URL fragments are not permitted")

    hostname = hostname.rstrip(".").lower()

    if hostname == "localhost" or hostname.endswith((".localhost", ".local", ".internal")):
        raise ValueError("Local or internal hostnames are not permitted")

    try:
        address = ipaddress.ip_address(hostname)
    except ValueError:
        pass
    else:
        if not address.is_global:
            raise ValueError("Private or non-public IP addresses are not permitted")


def validate_public_dns(hostname):
    """Reject hostnames resolving to non-public IP addresses.

    Intended for pre-activation checks, not registration.
    """
    import socket

    if not isinstance(hostname, str) or not hostname.strip():
        raise ValueError("Invalid DNS hostname")

    try:
        results = socket.getaddrinfo(
            hostname,
            None,
            type=socket.SOCK_STREAM,
        )
    except (socket.gaierror, OSError) as exc:
        raise ValueError("DNS resolution failed") from exc

    if not results:
        raise ValueError("DNS resolution returned no addresses")

    for result in results:
        address_text = result[4][0]

        try:
            address = ipaddress.ip_address(address_text)
        except ValueError as exc:
            raise ValueError("Invalid resolved IP address") from exc

        if not address.is_global:
            raise ValueError(
                "DNS hostname resolves to a non-public IP address"
            )

    return True
