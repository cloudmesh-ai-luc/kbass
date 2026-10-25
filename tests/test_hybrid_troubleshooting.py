"""Unit tests for hybrid AI-assisted troubleshooting."""

import unittest

from kbass_monitoring.hybrid_troubleshooting import analyze_incident_hybrid


class TestHybridTroubleshooting(unittest.TestCase):

    def setUp(self):
        self.incident = {
            "name": "ApplicationDown",
            "state": "firing",
        }

    def test_rule_based_fallback_without_ai(self):
        result = analyze_incident_hybrid(self.incident)

        self.assertEqual(result["diagnosis_type"], "rule_based")
        self.assertFalse(result["root_cause_confirmed"])

    def test_successful_ai_analysis(self):
        def fake_ai_analyzer(incident):
            return {
                "explanation": "The application is unreachable.",
                "possible_causes": ["The container may have stopped."],
                "recommended_actions": ["Inspect container logs."],
            }

        result = analyze_incident_hybrid(
            self.incident,
            ai_analyzer=fake_ai_analyzer,
        )

        self.assertEqual(result["diagnosis_type"], "ai_assisted")
        self.assertFalse(result["root_cause_confirmed"])
        self.assertEqual(
            result["explanation"],
            "The application is unreachable.",
        )

    def test_invalid_ai_response_uses_fallback(self):
        result = analyze_incident_hybrid(
            self.incident,
            ai_analyzer=lambda incident: {"explanation": "Incomplete"},
        )

        self.assertEqual(result["diagnosis_type"], "rule_based")

    def test_ai_exception_uses_fallback(self):
        def failing_ai_analyzer(incident):
            raise RuntimeError("AI service unavailable")

        result = analyze_incident_hybrid(
            self.incident,
            ai_analyzer=failing_ai_analyzer,
        )

        self.assertEqual(result["diagnosis_type"], "rule_based")


if __name__ == "__main__":
    unittest.main()


class TestHybridCaching(unittest.TestCase):

    def test_repeated_incident_reuses_ai_diagnosis(self):
        from kbass_monitoring.hybrid_troubleshooting import DiagnosisCache

        cache = DiagnosisCache(ttl_seconds=900, max_entries=100)
        calls = []

        def fake_ai_analyzer(incident):
            calls.append(incident["name"])
            return {
                "explanation": "The application may be unavailable.",
                "possible_causes": ["The process may have stopped."],
                "recommended_actions": ["Inspect application logs."],
            }

        incident = {
            "name": "ApplicationDown",
            "state": "firing",
            "active_at": "2026-10-19T20:00:00Z",
            "labels": {
                "alertname": "ApplicationDown",
                "instance": "app:8000",
            },
        }

        first = analyze_incident_hybrid(
            incident,
            ai_analyzer=fake_ai_analyzer,
            cache=cache,
        )

        second = analyze_incident_hybrid(
            incident,
            ai_analyzer=fake_ai_analyzer,
            cache=cache,
        )

        self.assertEqual(first, second)
        self.assertEqual(len(calls), 1)
        self.assertEqual(first["diagnosis_type"], "ai_assisted")

    def test_expired_diagnosis_is_not_reused(self):
        from unittest.mock import patch
        from kbass_monitoring.hybrid_troubleshooting import DiagnosisCache

        cache = DiagnosisCache(ttl_seconds=900, max_entries=100)

        with patch(
            "kbass_monitoring.diagnosis_cache.time.monotonic",
            return_value=1000,
        ):
            cache.set("incident-1", {"explanation": "Initial diagnosis"})

        with patch(
            "kbass_monitoring.diagnosis_cache.time.monotonic",
            return_value=1899,
        ):
            self.assertIsNotNone(cache.get("incident-1"))

        with patch(
            "kbass_monitoring.diagnosis_cache.time.monotonic",
            return_value=1900,
        ):
            self.assertIsNone(cache.get("incident-1"))

    def test_failed_ai_analysis_is_not_cached(self):
        from kbass_monitoring.hybrid_troubleshooting import DiagnosisCache

        cache = DiagnosisCache(ttl_seconds=900, max_entries=100)
        calls = []

        def unreliable_ai_analyzer(incident):
            calls.append(incident["name"])

            if len(calls) == 1:
                raise TimeoutError("AI provider temporarily unavailable")

            return {
                "explanation": "The application may be unavailable.",
                "possible_causes": ["The process may have stopped."],
                "recommended_actions": ["Inspect application logs."],
            }

        incident = {
            "name": "ApplicationDown",
            "state": "firing",
            "active_at": "2026-10-19T20:00:00Z",
        }

        first = analyze_incident_hybrid(
            incident,
            ai_analyzer=unreliable_ai_analyzer,
            cache=cache,
        )

        second = analyze_incident_hybrid(
            incident,
            ai_analyzer=unreliable_ai_analyzer,
            cache=cache,
        )

        third = analyze_incident_hybrid(
            incident,
            ai_analyzer=unreliable_ai_analyzer,
            cache=cache,
        )

        self.assertEqual(first["diagnosis_type"], "rule_based")
        self.assertEqual(second["diagnosis_type"], "ai_assisted")
        self.assertEqual(third, second)
        self.assertEqual(len(calls), 2)

    def test_concurrent_requests_share_one_ai_diagnosis(self):
        import threading
        import time
        from concurrent.futures import ThreadPoolExecutor
        from kbass_monitoring.hybrid_troubleshooting import DiagnosisCache

        cache = DiagnosisCache(ttl_seconds=900, max_entries=100)
        calls = []
        barrier = threading.Barrier(2)

        def slow_ai_analyzer(incident):
            calls.append(incident["name"])
            time.sleep(0.1)
            return {
                "explanation": "The application may be unavailable.",
                "possible_causes": ["The process may have stopped."],
                "recommended_actions": ["Inspect application logs."],
            }

        incident = {
            "name": "ApplicationDown",
            "state": "firing",
            "active_at": "2026-10-19T20:00:00Z",
        }

        def run_analysis():
            barrier.wait(timeout=5)
            return analyze_incident_hybrid(
                incident,
                ai_analyzer=slow_ai_analyzer,
                cache=cache,
            )

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(run_analysis)
                for _ in range(2)
            ]
            results = [future.result(timeout=10) for future in futures]

        self.assertEqual(results[0], results[1])
        self.assertEqual(results[0]["diagnosis_type"], "ai_assisted")
        self.assertEqual(len(calls), 1)


class TestHybridInferenceBudget(unittest.TestCase):

    def test_exhausted_budget_uses_rule_based_fallback(self):
        from kbass_monitoring.ai_budget import InferenceBudget
        from kbass_monitoring.diagnosis_cache import DiagnosisCache

        budget = InferenceBudget(max_requests=1, window_seconds=60)
        cache = DiagnosisCache(ttl_seconds=900, max_entries=100)
        calls = []

        def fake_ai_analyzer(incident):
            calls.append(incident["name"])
            return {
                "explanation": "AI-generated diagnosis.",
                "possible_causes": ["Application process failure."],
                "recommended_actions": ["Inspect application logs."],
            }

        first = analyze_incident_hybrid(
            {"name": "ApplicationDown", "active_at": "incident-1"},
            ai_analyzer=fake_ai_analyzer,
            cache=cache,
            budget=budget,
        )

        second = analyze_incident_hybrid(
            {"name": "HighErrorRate", "active_at": "incident-2"},
            ai_analyzer=fake_ai_analyzer,
            cache=cache,
            budget=budget,
        )

        self.assertEqual(first["diagnosis_type"], "ai_assisted")
        self.assertEqual(second["diagnosis_type"], "rule_based")
        self.assertEqual(len(calls), 1)
