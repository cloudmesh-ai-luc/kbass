"""Tests for graceful handling of Redis storage failures."""

import unittest
from unittest.mock import patch

from redis.exceptions import ConnectionError

from kbass_monitoring.app import app, limiter


class TestRedisStorageFailure(unittest.TestCase):

    def test_login_returns_503_when_storage_unavailable(self):
        storage = limiter.limiter.storage

        with patch.object(
            storage,
            "incr",
            side_effect=ConnectionError("Simulated Redis outage"),
        ):
            with app.test_client() as client:
                response = client.post(
                    "/api/auth/login",
                    json={"token": "invalid-test-token"},
                )

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.get_json(),
            {
                "error": "A required service is temporarily unavailable"
            },
        )

    def test_health_remains_available_during_storage_failure(self):
        storage = limiter.limiter.storage

        with patch.object(
            storage,
            "incr",
            side_effect=ConnectionError("Simulated Redis outage"),
        ):
            with app.test_client() as client:
                response = client.get("/health")

        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
