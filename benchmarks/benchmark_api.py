"""Benchmark HTTP API response times and throughput."""

import argparse
import json
import math
import statistics
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import urlopen


def send_request(url, timeout):
    start = time.perf_counter()

    try:
        with urlopen(url, timeout=timeout) as response:
            status = response.status
            response.read()
    except Exception as exc:
        return {
            "status": "error",
            "latency_ms": round(
                (time.perf_counter() - start) * 1000, 3
            ),
            "error": str(exc),
        }

    return {
        "status": status,
        "latency_ms": round(
            (time.perf_counter() - start) * 1000, 3
        ),
    }


def percentile(values, percentage):
    index = math.ceil(len(values) * percentage / 100) - 1
    return sorted(values)[max(0, index)]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--url",
        default="http://localhost:8000/health",
    )
    parser.add_argument("--requests", type=int, default=100)
    parser.add_argument("--workers", type=int, default=1)
    parser.add_argument("--timeout", type=float, default=5)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()

    if args.requests < 1 or args.workers < 1 or args.timeout <= 0:
        parser.error(
            "Requests, workers, and timeout must be positive."
        )

    started = datetime.now(timezone.utc).isoformat()
    start = time.perf_counter()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        results = list(
            executor.map(
                lambda _: send_request(args.url, args.timeout),
                range(args.requests),
            )
        )

    duration = time.perf_counter() - start

    successful = [
        result["latency_ms"]
        for result in results
        if result["status"] == 200
    ]

    summary = {
        "timestamp_utc": started,
        "url": args.url,
        "total_requests": args.requests,
        "workers": args.workers,
        "successful_requests": len(successful),
        "failed_requests": args.requests - len(successful),
        "duration_seconds": round(duration, 3),
        "throughput_rps": round(args.requests / duration, 2),
    }

    if successful:
        summary["latency_ms"] = {
            "minimum": round(min(successful), 2),
            "average": round(statistics.mean(successful), 2),
            "median": round(statistics.median(successful), 2),
            "p95": round(percentile(successful, 95), 2),
            "maximum": round(max(successful), 2),
        }

    print(json.dumps(summary, indent=2))

    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {"summary": summary, "requests": results},
                indent=2,
            )
            + "\n"
        )
        print(f"\nResults saved to: {path}")


if __name__ == "__main__":
    main()
