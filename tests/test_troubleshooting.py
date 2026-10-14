"""Unit tests for rule-based incident troubleshooting."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from troubleshooting import analyze_incident


class TestTroubleshooting(unittest.TestCase):

    def check_analysis(self, name):
        incident = {"name": name, "state": "firing"}
        result = analyze_incident(incident)

        self.assertEqual(result["diagnosis_type"], "rule_based")
        self.assertFalse(result["root_cause_confirmed"])
        self.assertTrue(result["explanation"])
        self.assertTrue(result["possible_causes"])
        self.assertTrue(result["recommended_actions"])

        return result

    def test_application_down(self):
        result = self.check_analysis("ApplicationDown")
        self.assertIn("Prometheus", result["explanation"])

    def test_high_error_rate(self):
        result = self.check_analysis("HighErrorRate")
        self.assertIn("5%", result["explanation"])

    def test_unknown_alert(self):
        result = self.check_analysis("HighMemoryUsage")
        self.assertIn("HighMemoryUsage", result["explanation"])


if __name__ == "__main__":
    unittest.main()
