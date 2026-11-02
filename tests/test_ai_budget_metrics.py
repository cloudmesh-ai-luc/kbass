"""Tests for Prometheus AI inference budget metrics."""

import unittest
from unittest.mock import Mock

from prometheus_client import REGISTRY

from kbass_monitoring.ai_metrics import record_ai_budget_decision
from kbass_monitoring.hybrid_troubleshooting import analyze_incident_hybrid
from kbass_monitoring.redis_ai_budget import InferenceBudgetUnavailable


class TestAIBudgetMetrics(unittest.TestCase):

    def setUp(self):
        self.incident = {
            "name": "ApplicationDown",
            "state": "firing",
        }
        self.ai_analyzer = Mock(return_value={
            "explanation": "Application unavailable.",
            "possible_causes": ["Process stopped."],
            "recommended_actions": ["Inspect logs."],
        })

    def metric_value(self, outcome):
        value = REGISTRY.get_sample_value(
            "cloudops_ai_budget_decisions_total",
            {"outcome": outcome},
        )
        return value or 0

    def test_allowed_budget_increments_counter(self):
        before = self.metric_value("allowed")
        budget = Mock()
        budget.try_acquire.return_value = True

        result = analyze_incident_hybrid(
            self.incident,
            ai_analyzer=self.ai_analyzer,
            budget=budget,
        )

        self.assertEqual(result["diagnosis_type"], "ai_assisted")
        self.assertEqual(self.metric_value("allowed"), before + 1)
        self.ai_analyzer.assert_called_once()

    def test_exhausted_budget_increments_counter(self):
        before = self.metric_value("exhausted")
        budget = Mock()
        budget.try_acquire.return_value = False

        result = analyze_incident_hybrid(
            self.incident,
            ai_analyzer=self.ai_analyzer,
            budget=budget,
        )

        self.assertEqual(result["diagnosis_type"], "rule_based")
        self.assertEqual(self.metric_value("exhausted"), before + 1)
        self.ai_analyzer.assert_not_called()

    def test_unavailable_budget_increments_counter(self):
        before = self.metric_value("unavailable")
        budget = Mock()
        budget.try_acquire.side_effect = InferenceBudgetUnavailable(
            "Simulated outage"
        )

        result = analyze_incident_hybrid(
            self.incident,
            ai_analyzer=self.ai_analyzer,
            budget=budget,
        )

        self.assertEqual(result["diagnosis_type"], "rule_based")
        self.assertEqual(self.metric_value("unavailable"), before + 1)
        self.ai_analyzer.assert_not_called()

    def test_invalid_outcome_is_rejected(self):
        with self.assertRaises(ValueError):
            record_ai_budget_decision("unexpected")


if __name__ == "__main__":
    unittest.main()
