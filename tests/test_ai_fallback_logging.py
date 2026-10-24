"""Tests for safe AI troubleshooting fallback logging."""

import unittest
from unittest.mock import patch

from kbass_monitoring.ai_budget import InferenceBudget
from kbass_monitoring.hybrid_troubleshooting import analyze_incident_hybrid


class TestAIFallbackLogging(unittest.TestCase):

    def setUp(self):
        self.incident = {
            "name": "ApplicationDown",
            "state": "firing",
        }

    def test_ai_exception_logs_without_sensitive_details(self):
        secret = "SENSITIVE_TEST_TOKEN_123"

        def failing_analyzer(incident):
            raise RuntimeError(f"Provider error: {secret}")

        with self.assertLogs(
            "kbass_monitoring.hybrid_troubleshooting",
            level="WARNING",
        ) as captured:
            result = analyze_incident_hybrid(
                self.incident,
                ai_analyzer=failing_analyzer,
            )

        self.assertEqual(result["diagnosis_type"], "rule_based")
        self.assertIn("ai_inference_failed", captured.output[0])
        self.assertNotIn(secret, "\n".join(captured.output))

    def test_invalid_response_logs_warning(self):
        with self.assertLogs(
            "kbass_monitoring.hybrid_troubleshooting",
            level="WARNING",
        ) as captured:
            result = analyze_incident_hybrid(
                self.incident,
                ai_analyzer=lambda incident: {"explanation": "Incomplete"},
            )

        self.assertEqual(result["diagnosis_type"], "rule_based")
        self.assertIn("invalid_ai_response", captured.output[0])

    def test_exhausted_budget_logs_warning(self):
        budget = InferenceBudget(max_requests=1, window_seconds=60)
        budget.try_acquire()

        with patch(
            "kbass_monitoring.hybrid_troubleshooting.analyze_with_ai"
        ) as analyzer:
            with self.assertLogs(
                "kbass_monitoring.hybrid_troubleshooting",
                level="WARNING",
            ) as captured:
                result = analyze_incident_hybrid(
                    self.incident,
                    ai_analyzer=analyzer,
                    budget=budget,
                )

        self.assertEqual(result["diagnosis_type"], "rule_based")
        self.assertIn("ai_budget_exhausted", captured.output[0])
        analyzer.assert_not_called()


if __name__ == "__main__":
    unittest.main()
