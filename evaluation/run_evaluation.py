"""Compare rule-based and AI-assisted incident troubleshooting."""

import argparse
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

from kbass_monitoring.troubleshooting import analyze_incident
from kbass_monitoring.hybrid_troubleshooting import analyze_incident_hybrid


BASE_DIR = Path(__file__).resolve().parent
DEFAULT_SCENARIOS_PATH = BASE_DIR / "scenarios.json"
RESULTS_DIR = BASE_DIR / "results"


def measure(function, incident):
    start = time.perf_counter()
    diagnosis = function(incident)
    elapsed = time.perf_counter() - start

    return {
        "latency_seconds": round(elapsed, 4),
        "diagnosis": diagnosis,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate CloudOps troubleshooting methods."
    )
    parser.add_argument(
        "--scenarios",
        type=Path,
        default=DEFAULT_SCENARIOS_PATH,
        help="Path to the evaluation scenarios JSON file.",
    )
    args = parser.parse_args()

    with args.scenarios.open(encoding="utf-8") as file:
        scenarios = json.load(file)

    results = []

    for scenario in scenarios:
        incident = {
            key: scenario[key]
            for key in ("name", "state", "summary", "description")
        }

        print(f"\nEvaluating {scenario['id']}: {scenario['name']}")

        rule_result = measure(analyze_incident, incident)

        # No cache: measure a fresh AI inference for each scenario.
        ai_result = measure(
            lambda item: analyze_incident_hybrid(
                item,
                ai_analyzer="configured",
            ),
            incident,
        )

        print(
            f"  Rule-based: "
            f"{rule_result['latency_seconds']:.4f}s"
        )
        print(
            f"  AI-assisted: "
            f"{ai_result['latency_seconds']:.4f}s "
            f"({ai_result['diagnosis']['diagnosis_type']})"
        )

        results.append({
            "scenario_id": scenario["id"],
            "alert_name": scenario["name"],
            "ground_truth_cause": scenario["ground_truth_cause"],
            "expected_actions": scenario["expected_actions"],
            "rule_based": rule_result,
            "ai_assisted": ai_result,
        })

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime(
        "%Y%m%dT%H%M%SZ"
    )

    output_path = RESULTS_DIR / f"evaluation_{timestamp}.json"

    report = {
        "dataset": str(args.scenarios),
        "timestamp_utc": timestamp,
        "provider": os.getenv("CLOUDOPS_AI_PROVIDER", "openai"),
        "model": os.getenv("CLOUDOPS_AI_MODEL"),
        "scenarios": results,
    }

    with output_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2)

    print(f"\nResults saved to: {output_path}")


if __name__ == "__main__":
    main()
