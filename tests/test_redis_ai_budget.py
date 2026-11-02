"""Tests for the Redis-backed AI inference budget."""

import unittest
from unittest.mock import patch

from redis.exceptions import ConnectionError

from kbass_monitoring.redis_ai_budget import (
    InferenceBudgetUnavailable,
    RedisInferenceBudget,
)


class TestRedisInferenceBudget(unittest.TestCase):

    @patch("kbass_monitoring.redis_ai_budget.Redis.from_url")
    def test_allows_requests_within_budget(self, mock_from_url):
        mock_client = mock_from_url.return_value
        mock_script = mock_client.register_script.return_value
        mock_script.side_effect = [1, 1, 0]

        budget = RedisInferenceBudget(
            redis_url="redis://localhost:6379/0",
            max_requests=2,
            window_seconds=60,
        )

        self.assertTrue(budget.try_acquire())
        self.assertTrue(budget.try_acquire())
        self.assertFalse(budget.try_acquire())

        self.assertEqual(mock_script.call_count, 3)

        for call in mock_script.call_args_list:
            self.assertEqual(
                call.kwargs["keys"],
                ["cloudops:ai:inference_budget"],
            )
            self.assertEqual(
                call.kwargs["args"][:2],
                [2, 60000],
            )

    @patch("kbass_monitoring.redis_ai_budget.Redis.from_url")
    def test_redis_failure_rejects_inference(self, mock_from_url):
        mock_script = (
            mock_from_url.return_value.register_script.return_value
        )
        mock_script.side_effect = ConnectionError("Redis unavailable")

        budget = RedisInferenceBudget(
            redis_url="redis://localhost:6379/0"
        )

        with self.assertRaises(InferenceBudgetUnavailable):
            budget.try_acquire()

    @patch("kbass_monitoring.redis_ai_budget.Redis.from_url")
    def test_redis_outage_does_not_log_budget_exhaustion(self, mock_from_url):
        from kbass_monitoring.hybrid_troubleshooting import analyze_incident_hybrid

        mock_script = mock_from_url.return_value.register_script.return_value
        mock_script.side_effect = ConnectionError("Redis unavailable")

        budget = RedisInferenceBudget(
            redis_url="redis://localhost:6379/0"
        )
        ai_calls = []

        def fake_ai_analyzer(incident):
            ai_calls.append(incident)
            return {"explanation": "Should not run"}

        with self.assertLogs(level="WARNING") as captured:
            result = analyze_incident_hybrid(
                {"name": "ApplicationDown", "state": "firing"},
                ai_analyzer=fake_ai_analyzer,
                budget=budget,
            )

        self.assertEqual(result["diagnosis_type"], "rule_based")
        self.assertEqual(ai_calls, [])
        self.assertTrue(
            any("redis_ai_budget_unavailable" in message
                for message in captured.output)
        )
        self.assertFalse(
            any("ai_budget_exhausted" in message
                for message in captured.output)
        )

    def test_invalid_configuration_rejected(self):
        for options in (
            {"redis_url": ""},
            {"redis_url": "redis://localhost:6379/0", "max_requests": 0},
            {"redis_url": "redis://localhost:6379/0", "window_seconds": 0},
        ):
            with self.subTest(options=options):
                with self.assertRaises(ValueError):
                    RedisInferenceBudget(**options)


if __name__ == "__main__":
    unittest.main()
