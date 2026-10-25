"""Unit tests for the optional AI troubleshooting client."""

import io
import json
import unittest
from unittest.mock import patch

from kbass_monitoring.ai_client import analyze_with_ai


class TestAIClient(unittest.TestCase):

    def setUp(self):
        self.incident = {
            "name": "ApplicationDown",
            "state": "firing",
        }

    @patch.dict("os.environ", {}, clear=True)
    def test_missing_configuration(self):
        with self.assertRaises(RuntimeError):
            analyze_with_ai(self.incident)

    @patch.dict(
        "os.environ",
        {
            "CLOUDOPS_AI_API_KEY": "test-key",
            "CLOUDOPS_AI_MODEL": "test-model",
        },
        clear=True,
    )
    @patch("kbass_monitoring.ai_client.urlopen")
    def test_successful_response(self, mock_urlopen):
        analysis = {
            "explanation": "The application is unreachable.",
            "possible_causes": ["The container may have stopped."],
            "recommended_actions": ["Inspect container logs."],
        }

        response = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(analysis),
                    }
                }
            ]
        }

        mock_urlopen.return_value.__enter__.return_value = io.BytesIO(
            json.dumps(response).encode("utf-8")
        )

        result = analyze_with_ai(self.incident)

        self.assertEqual(result, analysis)
        self.assertEqual(mock_urlopen.call_args.kwargs["timeout"], 5)

    @patch.dict(
        "os.environ",
        {
            "CLOUDOPS_AI_API_KEY": "test-key",
            "CLOUDOPS_AI_MODEL": "test-model",
        },
        clear=True,
    )
    @patch("kbass_monitoring.ai_client.urlopen")
    def test_api_failure(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError("Request timed out")

        with self.assertRaises(TimeoutError):
            analyze_with_ai(self.incident)

    @patch.dict(
        "os.environ",
        {
            "CLOUDOPS_AI_API_KEY": "test-key",
            "CLOUDOPS_AI_MODEL": "test-model",
            "CLOUDOPS_AI_ENDPOINT": "http://localhost:8080/api",
        },
        clear=True,
    )
    def test_custom_endpoint_rejected(self):
        with self.assertRaises(ValueError):
            analyze_with_ai(self.incident)


if __name__ == "__main__":
    unittest.main()


class TestOllamaAIClient(unittest.TestCase):

    @patch.dict(
        "os.environ",
        {
            "CLOUDOPS_AI_PROVIDER": "ollama",
            "CLOUDOPS_AI_MODEL": "qwen3:4b",
        },
        clear=True,
    )
    @patch("kbass_monitoring.ai_client.urlopen")
    def test_ollama_structured_response(self, mock_urlopen):
        analysis = {
            "explanation": "The application may be unavailable.",
            "possible_causes": ["The process may have stopped."],
            "recommended_actions": ["Inspect application logs."],
        }

        response = {
            "message": {
                "content": json.dumps(analysis),
            }
        }

        mock_urlopen.return_value.__enter__.return_value = io.BytesIO(
            json.dumps(response).encode("utf-8")
        )

        result = analyze_with_ai({
            "name": "ApplicationDown",
            "state": "firing",
        })

        self.assertEqual(result, analysis)

        request = mock_urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "http://127.0.0.1:11434/api/chat",
        )

        payload = json.loads(request.data)
        self.assertEqual(payload["model"], "qwen3:4b")
        schema = payload["format"]
        self.assertEqual(schema["type"], "object")
        self.assertEqual(
            set(schema["required"]),
            {
                "explanation",
                "possible_causes",
                "recommended_actions",
            },
        )
        self.assertFalse(schema["additionalProperties"])
        self.assertFalse(payload["think"])

    @patch.dict(
        "os.environ",
        {
            "CLOUDOPS_AI_PROVIDER": "ollama",
            "CLOUDOPS_AI_MODEL": "qwen3:4b",
            "CLOUDOPS_OLLAMA_URL": "http://host.docker.internal:11434",
        },
        clear=True,
    )
    @patch("kbass_monitoring.ai_client.urlopen")
    def test_ollama_docker_host_address(self, mock_urlopen):
        analysis = {
            "explanation": "The application may be unavailable.",
            "possible_causes": ["The application process stopped."],
            "recommended_actions": ["Inspect application logs."],
        }

        mock_urlopen.return_value.__enter__.return_value = io.BytesIO(
            json.dumps({
                "message": {"content": json.dumps(analysis)}
            }).encode("utf-8")
        )

        result = analyze_with_ai({
            "name": "ApplicationDown",
            "state": "firing",
        })

        self.assertEqual(result, analysis)
        request = mock_urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "http://host.docker.internal:11434/api/chat",
        )

    @patch.dict(
        "os.environ",
        {
            "CLOUDOPS_AI_PROVIDER": "ollama",
            "CLOUDOPS_AI_MODEL": "qwen3:4b",
            "CLOUDOPS_OLLAMA_URL": "http://example.com:11434",
        },
        clear=True,
    )
    @patch("kbass_monitoring.ai_client.urlopen")
    def test_ollama_rejects_unsupported_endpoint(self, mock_urlopen):
        with self.assertRaises(ValueError):
            analyze_with_ai({
                "name": "ApplicationDown",
                "state": "firing",
            })

        mock_urlopen.assert_not_called()
