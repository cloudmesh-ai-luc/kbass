"""Inspect Prometheus ApplicationDown alert state."""

import json
from datetime import datetime, timezone
from urllib.request import urlopen

PROMETHEUS_URL = "http://localhost:9090/api/v1/rules"
ALERT_NAME = "ApplicationDown"


def get_alert_state():
    with urlopen(PROMETHEUS_URL, timeout=5) as response:
        payload = json.load(response)

    if payload.get("status") != "success":
        raise RuntimeError("Prometheus API returned an unsuccessful response")

    for group in payload["data"]["groups"]:
        for rule in group["rules"]:
            if rule.get("name") == ALERT_NAME:
                return {
                    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                    "alert": ALERT_NAME,
                    "state": rule["state"],
                    "health": rule["health"],
                    "active_alerts": rule.get("alerts", []),
                }

    raise RuntimeError(f"Alert rule not found: {ALERT_NAME}")


if __name__ == "__main__":
    print(json.dumps(get_alert_state(), indent=2))
