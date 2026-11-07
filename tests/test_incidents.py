"""Automated tests for the Flask incident API."""

import sys
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError


from kbass_monitoring.app import app


class TestIncidentAPI(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_no_active_alerts(self):
        with patch("kbass_monitoring.app.fetch_prometheus_alerts", return_value=[]):
            response = self.client.get("/api/incidents")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["status"], "success")
        self.assertEqual(data["count"], 0)
        self.assertEqual(data["incidents"], [])

    def test_application_down(self):
        alert = {
            "labels": {
                "alertname": "ApplicationDown",
                "severity": "critical",
                "instance": "app:8000",
            },
            "annotations": {
                "summary": "Flask application is down",
            },
            "state": "firing",
            "activeAt": "2026-10-14T16:04:36Z",
            "value": "0e+00",
        }

        with patch("kbass_monitoring.app.fetch_prometheus_alerts", return_value=[alert]):
            response = self.client.get("/api/incidents")

        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data["count"], 1)

        incident = data["incidents"][0]
        self.assertEqual(incident["name"], "ApplicationDown")
        self.assertEqual(incident["severity"], "critical")
        self.assertEqual(incident["state"], "firing")
        self.assertEqual(
            incident["analysis"]["diagnosis_type"], "rule_based"
        )
        self.assertFalse(
            incident["analysis"]["root_cause_confirmed"]
        )
        self.assertTrue(
            incident["analysis"]["recommended_actions"]
        )

    def test_high_error_rate(self):
        alert = {
            "labels": {
                "alertname": "HighErrorRate",
                "severity": "warning",
            },
            "annotations": {
                "summary": "High HTTP server error rate",
            },
            "state": "firing",
            "value": "0.12",
        }

        with patch("kbass_monitoring.app.fetch_prometheus_alerts", return_value=[alert]):
            response = self.client.get("/api/incidents")

        self.assertEqual(response.status_code, 200)
        incident = response.get_json()["incidents"][0]
        self.assertEqual(incident["name"], "HighErrorRate")
        self.assertEqual(incident["severity"], "warning")
        self.assertTrue(
            incident["analysis"]["possible_causes"]
        )

    def test_resource_usage_alerts(self):
        for name, threshold in (
            ("HighCPUUsage", "80%"),
            ("HighMemoryUsage", "512 MiB"),
        ):
            with self.subTest(alert=name):
                alert = {
                    "labels": {
                        "alertname": name,
                        "severity": "warning",
                        "id": "/docker/example",
                    },
                    "annotations": {
                        "summary": f"{name} detected",
                    },
                    "state": "firing",
                }

                with patch(
                    "kbass_monitoring.app.fetch_prometheus_alerts",
                    return_value=[alert],
                ), patch.dict(
                    "os.environ",
                    {"CLOUDOPS_AI_ENABLED": "false"},
                ):
                    response = self.client.get("/api/incidents")

                self.assertEqual(response.status_code, 200)
                data = response.get_json()
                self.assertEqual(data["count"], 1)

                incident = data["incidents"][0]
                analysis = incident["analysis"]

                self.assertEqual(incident["name"], name)
                self.assertEqual(incident["severity"], "warning")
                self.assertEqual(incident["state"], "firing")
                self.assertIn(threshold, analysis["explanation"])
                self.assertEqual(
                    analysis["diagnosis_type"], "rule_based"
                )
                self.assertFalse(analysis["root_cause_confirmed"])
                self.assertTrue(analysis["possible_causes"])
                self.assertTrue(analysis["recommended_actions"])

    def test_unknown_alert(self):
        alert = {
            "labels": {
                "alertname": "UnknownAlert",
                "severity": "warning",
            },
            "annotations": {},
            "state": "firing",
        }

        with patch(
            "kbass_monitoring.app.fetch_prometheus_alerts",
            return_value=[alert],
        ), patch.dict(
            "os.environ",
            {"CLOUDOPS_AI_ENABLED": "false"},
        ):
            response = self.client.get("/api/incidents")

        self.assertEqual(response.status_code, 200)
        incident = response.get_json()["incidents"][0]
        self.assertEqual(incident["name"], "UnknownAlert")
        self.assertIn(
            "UnknownAlert", incident["analysis"]["explanation"]
        )
        self.assertFalse(
            incident["analysis"]["root_cause_confirmed"]
        )

    def test_prometheus_unavailable(self):
        with patch(
            "kbass_monitoring.app.fetch_prometheus_alerts",
            side_effect=URLError("Connection refused"),
        ):
            response = self.client.get("/api/incidents")

        self.assertEqual(response.status_code, 503)
        data = response.get_json()
        self.assertEqual(data["status"], "unavailable")
        self.assertNotIn("Connection refused", str(data))


if __name__ == "__main__":
    unittest.main()
