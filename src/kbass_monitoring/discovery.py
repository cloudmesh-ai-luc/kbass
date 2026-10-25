"""Prometheus service discovery for registered applications."""

from urllib.parse import urlsplit

from .registry import list_applications


def build_target_groups(applications):
    """Build Prometheus target groups without activating them."""
    groups = []

    for application in applications:
        if not application["enabled"]:
            continue

        metrics_url = application["metrics_url"]

        if not metrics_url:
            continue

        parsed = urlsplit(metrics_url)

        # The initial integration supports HTTPS on the standard port
        # and the conventional /metrics path only.
        if parsed.scheme != "https":
            continue

        if parsed.port not in (None, 443):
            continue

        if parsed.path != "/metrics" or parsed.query:
            continue

        groups.append({
            "targets": [parsed.hostname],
            "labels": {
                "application_id": str(application["id"]),
                "application_name": application["name"],
                "environment": application["environment"],
            },
        })

    return groups


def preview_registered_targets():
    """Return a discovery preview without writing target files."""
    return build_target_groups(list_applications())


def build_approved_target_groups(applications):
    """Generate targets only for explicitly approved applications.

    This function does not write target files or activate monitoring.
    """
    approved_applications = [
        application
        for application in applications
        if application.get("monitoring_approved") == 1
    ]

    return build_target_groups(approved_applications)


def write_approved_targets(applications, destination):
    """Atomically write approved Prometheus targets to a JSON file.

    Only approved and eligible applications are included.
    This function writes the file but does not itself initiate scraping.
    """
    import json
    import os
    import tempfile
    from pathlib import Path

    destination = Path(destination)
    groups = build_approved_target_groups(applications)

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=".targets-",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = temporary_file.name
            json.dump(groups, temporary_file, indent=2)
            temporary_file.write("\n")
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, destination)

    finally:
        if temporary_path is not None and os.path.exists(temporary_path):
            os.unlink(temporary_path)

    return len(groups)


def validate_activation_targets(applications):
    """Validate approved targets before potential monitoring activation.

    Performs DNS checks but does not write files or activate scraping.
    DNS validation alone does not prevent DNS rebinding.
    """
    from .validation import validate_public_dns

    groups = build_approved_target_groups(applications)

    for group in groups:
        for hostname in group["targets"]:
            validate_public_dns(hostname)

    return groups
