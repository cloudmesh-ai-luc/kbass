"""Tests for safe Prometheus discovery target-file updates."""

import json

from kbass_monitoring.discovery import build_approved_target_groups


def make_application(application_id, approved):
    return {
        "id": application_id,
        "name": f"Application {application_id}",
        "environment": "aws",
        "enabled": 1,
        "monitoring_approved": int(approved),
        "metrics_url": f"https://app{application_id}.example.com/metrics",
    }


def test_writer_creates_valid_json(tmp_path):
    from kbass_monitoring.discovery import write_approved_targets

    destination = tmp_path / "registered-apps.json"
    applications = [make_application(1, True)]

    count = write_approved_targets(applications, destination)

    assert count == 1
    assert json.loads(destination.read_text()) == (
        build_approved_target_groups(applications)
    )


def test_writer_excludes_unapproved_applications(tmp_path):
    from kbass_monitoring.discovery import write_approved_targets

    destination = tmp_path / "registered-apps.json"
    applications = [
        make_application(1, False),
        make_application(2, True),
    ]

    count = write_approved_targets(applications, destination)
    groups = json.loads(destination.read_text())

    assert count == 1
    assert groups[0]["labels"]["application_id"] == "2"


def test_writer_replaces_existing_file(tmp_path):
    from kbass_monitoring.discovery import write_approved_targets

    destination = tmp_path / "registered-apps.json"
    destination.write_text('[{"targets":["old.example.com"]}]')

    count = write_approved_targets([], destination)

    assert count == 0
    assert json.loads(destination.read_text()) == []


def test_writer_leaves_no_temporary_files(tmp_path):
    from kbass_monitoring.discovery import write_approved_targets

    destination = tmp_path / "registered-apps.json"

    write_approved_targets([make_application(1, True)], destination)

    assert sorted(path.name for path in tmp_path.iterdir()) == [
        "registered-apps.json"
    ]
