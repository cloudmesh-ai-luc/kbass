"""Read-only smoke tests for the CloudOps AI Docker Compose stack."""

import json
import subprocess
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def check_http(name, url, expected_status=200, validator=None):
    try:
        with urlopen(url, timeout=5) as response:
            body = response.read()
            if response.status != expected_status:
                raise ValueError(f"HTTP {response.status}")

            if validator is not None and not validator(body):
                raise ValueError("Unexpected response content")

        print(f"PASS: {name}")
        return True
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as exc:
        print(f"FAIL: {name} ({exc})")
        return False


def check_redis():
    try:
        result = subprocess.run(
            ["docker", "compose", "exec", "-T", "redis", "redis-cli", "ping"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
        if result.stdout.strip() != "PONG":
            raise ValueError("Redis did not return PONG")

        print("PASS: Redis")
        return True
    except (subprocess.CalledProcessError, OSError, TimeoutError, ValueError) as exc:
        print(f"FAIL: Redis ({exc})")
        return False


def flask_healthy(body):
    return json.loads(body).get("status") == "healthy"


def prometheus_ready(body):
    return body.decode().strip() == "Prometheus Server is Ready."


def grafana_healthy(body):
    return json.loads(body).get("database") == "ok"


def main():
    print("CloudOps AI — Deployment Smoke Test")
    print("-----------------------------------")

    results = [
        check_http(
            "Flask",
            "http://127.0.0.1:8000/health",
            validator=flask_healthy,
        ),
        check_http(
            "Prometheus",
            "http://127.0.0.1:9090/-/ready",
            validator=prometheus_ready,
        ),
        check_http(
            "Grafana",
            "http://127.0.0.1:3000/api/health",
            validator=grafana_healthy,
        ),
        check_http(
            "cAdvisor",
            "http://127.0.0.1:8081/healthz",
        ),
        check_redis(),
    ]

    passed = sum(results)
    print(f"\nResults: {passed}/{len(results)} checks passed")

    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
