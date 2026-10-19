# API Performance Evaluation

## 1. Objective

Evaluate the response time, throughput, and reliability of the
containerized Flask application's `/health` endpoint under sequential
and concurrent HTTP workloads.

These experiments support Phase 4 of the AI-Assisted Cloud Monitoring
and Troubleshooting Dashboard project.

## 2. Test Environment

- Application: Python/Flask
- Deployment: Local Docker Compose
- Monitoring: Prometheus and Grafana
- Endpoint: `http://localhost:8000/health`
- Benchmark client: Python standard library
- Execution: Local macOS host
- Server: Flask development server
- Date: October 16, 2026 (Chicago local time)

The benchmark measures client-observed HTTP response times, including
local networking and request-processing overhead.

## 3. Methodology

The reusable script `benchmark_api.py` sends HTTP requests and records:

- Successful and failed requests
- Minimum, average, and median response latency
- P95 and maximum latency
- Total execution duration
- Request throughput

Three initial configurations were evaluated:

1. Sequential baseline: 100 requests, 1 worker
2. Concurrent baseline: 100 requests, 10 workers
3. Concurrent load: 1,000 requests, 10 workers

A longer experiment repeatedly executed batches of 1,000 requests
with 10 workers for approximately 30 seconds.

Each batch used a separate thread pool. The sustained experiment
included process startup and inter-batch overhead in its overall
duration and throughput measurement.

## 4. Experimental Results

### 4.1 Initial Benchmarks

| Metric | Sequential | Concurrent | Larger Load |
|---|---:|---:|---:|
| Requests | 100 | 100 | 1,000 |
| Workers | 1 | 10 | 10 |
| Successful | 100 | 100 | 1,000 |
| Failed | 0 | 0 | 0 |
| Average latency (ms) | 3.35 | 9.95 | 7.47 |
| Median latency (ms) | 2.70 | 6.99 | 6.87 |
| P95 latency (ms) | 5.29 | 34.77 | 10.28 |
| Maximum latency (ms) | 25.13 | 40.51 | 40.52 |
| Throughput (req/s) | 297.26 | 969.02 | 1,330.52 |

### 4.2 Sustained Load Experiment

| Metric | Result |
|---|---:|
| Duration | 31.00 seconds |
| Benchmark batches | 29 |
| Concurrent workers | 10 |
| Total requests | 29,000 |
| Successful requests | 29,000 |
| Failed requests | 0 |
| Overall throughput | 935.61 req/s |
| Minimum latency | 2.96 ms |
| Average latency | 9.75 ms |
| Median latency | 7.88 ms |
| P95 latency | 17.61 ms |
| P99 latency | 26.67 ms |
| Maximum latency | 46.90 ms |

## 5. Observations

All requests returned HTTP 200 across the recorded experiments.

Concurrent workloads achieved higher observed throughput than the
sequential baseline, while also increasing request latency.

The 31-second experiment achieved approximately 935.61 requests per
second with no recorded failures.

The difference between short and longer experiments indicates that
single, short benchmark runs should not be treated as reliable
estimates of sustained application capacity.

## 6. Limitations

- Experiments were conducted locally, not on cloud infrastructure.
- The `/health` endpoint performs minimal application work.
- The application uses Flask's development server.
- Measurements include client and local networking overhead.
- Tests were not repeated across multiple independent trials.
- System resource utilization was not recorded.
- The sustained workload consisted of repeated short batches.
- Exact Prometheus alert detection and recovery latencies remain
  unmeasured.

These results characterize the tested configuration only and should
not be interpreted as production performance guarantees.

## 7. Reproducing the Benchmarks

Sequential baseline:

    python benchmarks/benchmark_api.py --requests 100 --workers 1

Concurrent baseline:

    python benchmarks/benchmark_api.py --requests 100 --workers 10

Larger concurrent load:

    python benchmarks/benchmark_api.py --requests 1000 --workers 10

To save individual measurements, add:

    --output benchmarks/results/experiment.json

Generated JSON results are excluded from Git by
`benchmarks/.gitignore`.

## 8. Next Steps

- Repeat experiments across multiple trials.
- Evaluate longer continuous workloads.
- Record CPU and memory utilization.
- Measure Prometheus alert detection and recovery latency.
- Compare local and cloud deployment performance.
- Evaluate API performance with a production WSGI server.
