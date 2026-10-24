"""Integration tests for hybrid AI troubleshooting in the incident API."""

import unittest
from unittest.mock import patch

from kbass_monitoring.app import app, diagnosis_cache


class TestHybridIncidentAPI(unittest.TestCase):

    def setUp(self):
        diagnosis_cache.clear()
        self.client = app.test_client()
        self.alert = {
            "labels": {
                "alertname": "ApplicationDown",
                "severity": "critical",
            },
            "annotations": {
                "summary": "Application unavailable",
            },
            "state": "firing",
        }

    @patch.dict("os.environ", {"CLOUDOPS_AI_ENABLED": "true"})
    @patch("kbass_monitoring.app.fetch_prometheus_alerts")
    @patch("kbass_monitoring.hybrid_troubleshooting.analyze_with_ai")
    def test_ai_enabled(self, mock_ai, mock_alerts):
        mock_alerts.return_value = [self.alert]
        mock_ai.return_value = {
            "explanation": "The application is unreachable.",
            "possible_causes": ["Container failure."],
            "recommended_actions": ["Inspect container logs."],
        }

        response = self.client.get("/api/incidents")
        self.assertEqual(response.status_code, 200)

        analysis = response.get_json()["incidents"][0]["analysis"]

        self.assertEqual(analysis["diagnosis_type"], "ai_assisted")
        self.assertFalse(analysis["root_cause_confirmed"])
        mock_ai.assert_called_once()

    @patch.dict("os.environ", {"CLOUDOPS_AI_ENABLED": "true"})
    @patch("kbass_monitoring.app.fetch_prometheus_alerts")
    @patch("kbass_monitoring.hybrid_troubleshooting.analyze_with_ai")
    def test_ai_failure_fallback(self, mock_ai, mock_alerts):
        mock_alerts.return_value = [self.alert]
        mock_ai.side_effect = TimeoutError("AI unavailable")

        response = self.client.get("/api/incidents")
        self.assertEqual(response.status_code, 200)

        analysis = response.get_json()["incidents"][0]["analysis"]

        self.assertEqual(analysis["diagnosis_type"], "rule_based")
        self.assertFalse(analysis["root_cause_confirmed"])

    @patch.dict("os.environ", {"CLOUDOPS_AI_ENABLED": "false"})
    @patch("kbass_monitoring.app.fetch_prometheus_alerts")
    @patch("kbass_monitoring.hybrid_troubleshooting.analyze_with_ai")
    def test_ai_disabled(self, mock_ai, mock_alerts):
        mock_alerts.return_value = [self.alert]

        response = self.client.get("/api/incidents")
        self.assertEqual(response.status_code, 200)

        analysis = response.get_json()["incidents"][0]["analysis"]

        self.assertEqual(analysis["diagnosis_type"], "rule_based")
        mock_ai.assert_not_called()


    @patch.dict("os.environ", {"CLOUDOPS_AI_ENABLED": "true"})
    @patch("kbass_monitoring.app.fetch_prometheus_alerts")
    @patch("kbass_monitoring.hybrid_troubleshooting.analyze_with_ai")
    def test_cached_diagnosis_does_not_consume_extra_budget(
        self, mock_ai, mock_alerts
    ):
        from kbass_monitoring.ai_budget import InferenceBudget

        mock_alerts.return_value = [self.alert]
        mock_ai.return_value = {
            "explanation": "The application may be unavailable.",
            "possible_causes": ["Container failure."],
            "recommended_actions": ["Inspect container logs."],
        }

        budget = InferenceBudget(max_requests=1, window_seconds=60)

        with patch("kbass_monitoring.app.inference_budget", budget):
            first = self.client.get("/api/incidents")
            second = self.client.get("/api/incidents")

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)

        first_analysis = first.get_json()["incidents"][0]["analysis"]
        second_analysis = second.get_json()["incidents"][0]["analysis"]

        self.assertEqual(first_analysis, second_analysis)
        self.assertEqual(first_analysis["diagnosis_type"], "ai_assisted")
        mock_ai.assert_called_once()


    @patch.dict("os.environ", {"CLOUDOPS_AI_ENABLED": "true"})
    @patch("kbass_monitoring.app.fetch_prometheus_alerts")
    @patch("kbass_monitoring.hybrid_troubleshooting.analyze_with_ai")
    def test_exhausted_budget_uses_rule_based_fallback(
        self, mock_ai, mock_alerts
    ):
        from kbass_monitoring.ai_budget import InferenceBudget

        mock_ai.return_value = {
            "explanation": "AI-generated diagnosis.",
            "possible_causes": ["Application process failure."],
            "recommended_actions": ["Inspect application logs."],
        }

        budget = InferenceBudget(max_requests=1, window_seconds=60)

        with patch("kbass_monitoring.app.inference_budget", budget):
            mock_alerts.return_value = [self.alert]
            first = self.client.get("/api/incidents")

            second_alert = {
                **self.alert,
                "labels": {
                    "alertname": "HighErrorRate",
                    "severity": "warning",
                },
            }
            mock_alerts.return_value = [second_alert]
            second = self.client.get("/api/incidents")

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)

        first_analysis = first.get_json()["incidents"][0]["analysis"]
        second_analysis = second.get_json()["incidents"][0]["analysis"]

        self.assertEqual(first_analysis["diagnosis_type"], "ai_assisted")
        self.assertEqual(second_analysis["diagnosis_type"], "rule_based")
        mock_ai.assert_called_once()


if __name__ == "__main__":
    unittest.main()
