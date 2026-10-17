import unittest
from unittest.mock import patch

from kbass_monitoring.app import app


class TestErrorSimulation(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_disabled_by_default(self):
        with patch.dict("os.environ", {}, clear=True):
            response = self.client.get("/test/error")
        self.assertEqual(response.status_code, 404)

    def test_enabled_from_loopback(self):
        with patch.dict("os.environ", {"ENABLE_ERROR_SIMULATION": "true"}):
            response = self.client.get(
                "/test/error",
                environ_overrides={"REMOTE_ADDR": "127.0.0.1"},
            )
        self.assertEqual(response.status_code, 500)

    def test_enabled_from_nonlocal_address(self):
        with patch.dict("os.environ", {"ENABLE_ERROR_SIMULATION": "true"}):
            response = self.client.get(
                "/test/error",
                environ_overrides={"REMOTE_ADDR": "192.0.2.10"},
            )
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
