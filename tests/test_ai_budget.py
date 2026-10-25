"""Tests for the AI inference request budget."""

import unittest
from unittest.mock import patch

from kbass_monitoring.ai_budget import InferenceBudget


class TestInferenceBudget(unittest.TestCase):

    def test_allows_requests_within_budget(self):
        budget = InferenceBudget(max_requests=2, window_seconds=60)

        with patch("kbass_monitoring.ai_budget.time.monotonic", return_value=100):
            self.assertTrue(budget.try_acquire())
            self.assertTrue(budget.try_acquire())
            self.assertFalse(budget.try_acquire())

    def test_budget_resets_after_window(self):
        budget = InferenceBudget(max_requests=1, window_seconds=60)

        with patch("kbass_monitoring.ai_budget.time.monotonic", return_value=100):
            self.assertTrue(budget.try_acquire())
            self.assertFalse(budget.try_acquire())

        with patch("kbass_monitoring.ai_budget.time.monotonic", return_value=160):
            self.assertTrue(budget.try_acquire())

    def test_invalid_configuration_rejected(self):
        with self.assertRaises(ValueError):
            InferenceBudget(max_requests=0, window_seconds=60)

        with self.assertRaises(ValueError):
            InferenceBudget(max_requests=10, window_seconds=0)
