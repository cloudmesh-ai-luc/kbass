# Prometheus Alert Detection and Recovery Latency

## 1. Objective

Measure how quickly Prometheus detects a Flask application failure
and clears the ApplicationDown alert after the application restarts.

## 2. Test Environment

- Application: Containerized Python/Flask service
- Monitoring: Prometheus
- Deployment: Local Docker Compose
- Alert: ApplicationDown
- Alert expression: up{job="flask-app"} == 0
- Alert duration: 15 seconds
- Prometheus scrape interval: 5 seconds
- Prometheus evaluation interval: 5 seconds
- Measurement polling interval: 0.5 seconds
- Experiment date: October 17, 2026 (Chicago local time)

## 3. Methodology

Each trial followed these steps:

1. Confirm ApplicationDown is healthy and inactive.
2. Record the application shutdown initiation timestamp.
3. Stop the Flask container using Docker Compose.
4. Record the shutdown command completion timestamp.
5. Poll the Prometheus rules API until ApplicationDown is firing.
6. Restart the Flask container.
7. Record the restart command completion timestamp.
8. Poll Prometheus until ApplicationDown becomes inactive.
9. Save the observed timestamps and calculated latencies.

Detection latency is measured from completion of the Docker stop
command to the first observation of the firing alert.

Recovery latency is measured from completion of the Docker start
command to the first observation of the inactive alert.

## 4. Experimental Results

| Metric | Trial 1 | Trial 2 | Trial 3 |
|---|---:|---:|---:|
| Detection latency (s) | 26.171 | 24.147 | 23.657 |
| Recovery latency (s) | 9.795 | 9.275 | 9.787 |
| Detection from stop initiation (s) | 29.545 | 27.504 | 27.101 |

### Summary Statistics

| Metric | Detection | Recovery |
|---|---:|---:|
| Mean latency | 24.658 s | 9.619 s |
| Minimum latency | 23.657 s | 9.275 s |
| Maximum latency | 26.171 s | 9.795 s |

All three experiments completed successfully.

After the third experiment, Flask returned HTTP 200, and
Prometheus reported ApplicationDown as inactive and healthy.

## 5. Interpretation

The observed detection latency ranged from approximately
23.7 to 26.2 seconds after the Docker stop command completed.

The observed recovery latency ranged from approximately
9.3 to 9.8 seconds after the Docker start command completed.

These measurements are consistent with the configured scrape
interval, evaluation interval, and alert duration.

## 6. Limitations

- Only three trials were conducted.
- Tests were performed in a local Docker environment.
- The experiment polls Prometheus every 0.5 seconds.
- Docker command completion does not necessarily coincide with
  the exact application failure or recovery timestamp.
- The measurements represent client-observed alert transitions,
  not exact internal Prometheus event timings.
- The experiment does not measure notification delivery latency.
- The results should not be treated as production guarantees.

## 7. Reproduction

Inspect the current alert state:

    python benchmarks/alert_latency/measure_alert.py

Run the controlled failure and recovery experiment:

    python benchmarks/alert_latency/run_experiment.py

The experiment temporarily stops the Flask application and
automatically attempts to restart it.

Future runs generate timestamped JSON results in
`benchmarks/results/`, which is excluded from Git.

## 8. Future Work

- Conduct additional trials.
- Record Prometheus internal alert timestamps.
- Measure application health recovery independently.
- Evaluate alert notification delivery latency.
- Compare local and cloud deployment results.
- Evaluate alert latency under concurrent application load.
