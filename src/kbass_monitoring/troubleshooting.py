"""Read-only, rule-based incident troubleshooting recommendations."""


def analyze_incident(incident):
    """Return an explanation and diagnostic guidance for an incident."""
    name = incident.get("name", "UnknownAlert")
    state = incident.get("state", "unknown")

    if name == "ApplicationDown":
        return {
            "explanation": (
                "Prometheus cannot scrape the monitored application. "
                "The application may be stopped, unreachable, or unable "
                "to respond to monitoring requests."
            ),
            "possible_causes": [
                "The application process or container has stopped.",
                "A network or DNS connectivity problem exists.",
                "The application is listening on the wrong port.",
                "The application is overloaded or unresponsive.",
            ],
            "recommended_actions": [
                "Check whether the application container is running.",
                "Inspect the application logs for errors.",
                "Verify network connectivity and the configured port.",
                "Check the Prometheus target status.",
            ],
            "diagnosis_type": "rule_based",
            "root_cause_confirmed": False,
        }

    if name == "HighErrorRate":
        return {
            "explanation": (
                "More than 5% of monitored HTTP requests returned "
                "server errors during the configured evaluation period."
            ),
            "possible_causes": [
                "Unhandled application exceptions.",
                "Database or external service failures.",
                "Incorrect application configuration.",
                "Resource exhaustion or application overload.",
            ],
            "recommended_actions": [
                "Inspect application logs for HTTP 5xx errors.",
                "Review recent deployments or configuration changes.",
                "Check CPU, memory, and application performance.",
                "Verify dependent services are available.",
            ],
            "diagnosis_type": "rule_based",
            "root_cause_confirmed": False,
        }

    if name == "HighCPUUsage":
        return {
            "explanation": (
                "A monitored container has exceeded the configured "
                "CPU usage threshold of 80% of one CPU core."
            ),
            "possible_causes": [
                "Increased application traffic or workload.",
                "CPU-intensive processing or background tasks.",
                "Inefficient code or excessive computation.",
                "A process consuming CPU unexpectedly.",
            ],
            "recommended_actions": [
                "Identify the affected container in Grafana.",
                "Inspect container CPU usage with docker stats.",
                "Review application logs and recent workload changes.",
                "Investigate CPU-intensive processes before scaling.",
            ],
            "diagnosis_type": "rule_based",
            "root_cause_confirmed": False,
        }

    if name == "HighMemoryUsage":
        return {
            "explanation": (
                "A monitored container has exceeded the configured "
                "memory working-set threshold of 512 MiB."
            ),
            "possible_causes": [
                "Increased application workload or memory demand.",
                "Memory retained longer than expected.",
                "Large in-memory datasets or caches.",
                "A possible application memory leak.",
            ],
            "recommended_actions": [
                "Identify the affected container in Grafana.",
                "Inspect memory consumption with docker stats.",
                "Review application logs for memory-related errors.",
                "Investigate sustained memory growth before restarting.",
            ],
            "diagnosis_type": "rule_based",
            "root_cause_confirmed": False,
        }

    return {
        "explanation": (
            f"The monitoring system reported {name} "
            f"with the current state '{state}'."
        ),
        "possible_causes": [
            "The underlying cause has not yet been determined."
        ],
        "recommended_actions": [
            "Review the alert description and associated metrics.",
            "Inspect relevant application and infrastructure logs.",
        ],
        "diagnosis_type": "rule_based",
        "root_cause_confirmed": False,
    }
