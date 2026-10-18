"""Measure Prometheus ApplicationDown detection and recovery latency."""

import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from measure_alert import get_alert_state

POLL_INTERVAL = 0.5
TIMEOUT = 90


def timestamp():
    return datetime.now(timezone.utc).isoformat()


def docker(*args):
    subprocess.run(
        ["docker", "compose", *args],
        check=True,
        timeout=60,
    )


def wait_for_state(target, timeout=TIMEOUT):
    start = time.monotonic()

    while time.monotonic() - start < timeout:
        alert = get_alert_state()

        if alert["state"] == target:
            return alert

        time.sleep(POLL_INTERVAL)

    raise TimeoutError(
        f"ApplicationDown did not reach '{target}' within {timeout}s"
    )


def main():
    initial = get_alert_state()

    if initial["health"] != "ok" or initial["state"] != "inactive":
        raise RuntimeError(
            "ApplicationDown must be healthy and inactive before testing."
        )

    results = {
        "experiment": "ApplicationDown detection and recovery",
        "poll_interval_seconds": POLL_INTERVAL,
        "started_utc": timestamp(),
    }

    app_stopped = False

    try:
        print("Stopping Flask application...", flush=True)

        stop_start = time.monotonic()
        results["stop_command_started_utc"] = timestamp()
        app_stopped = True
        docker("stop", "app")
        results["stop_command_completed_utc"] = timestamp()
        stop_completed = time.monotonic()

        print("Waiting for ApplicationDown to fire...", flush=True)
        firing = wait_for_state("firing")
        firing_observed = time.monotonic()

        results["firing_observed_utc"] = firing["timestamp_utc"]
        results["detection_latency_seconds"] = round(
            firing_observed - stop_completed, 3
        )
        results["detection_from_stop_start_seconds"] = round(
            firing_observed - stop_start, 3
        )

        print("Restarting Flask application...", flush=True)

        results["start_command_started_utc"] = timestamp()
        docker("start", "app")
        results["start_command_completed_utc"] = timestamp()
        start_completed = time.monotonic()
        app_stopped = False

        print("Waiting for ApplicationDown to resolve...", flush=True)
        inactive = wait_for_state("inactive")
        inactive_observed = time.monotonic()

        results["inactive_observed_utc"] = inactive["timestamp_utc"]
        results["recovery_latency_seconds"] = round(
            inactive_observed - start_completed, 3
        )

    finally:
        if app_stopped:
            print("Restoring Flask application...", flush=True)
            docker("start", "app")

    results["completed_utc"] = timestamp()

    run_id = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    output = Path(
        f"benchmarks/results/alert_latency_{run_id}.json"
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(results, indent=2) + "\n")

    print("\nExperiment results:")
    print(json.dumps(results, indent=2))
    print(f"\nResults saved to: {output}")


if __name__ == "__main__":
    main()
