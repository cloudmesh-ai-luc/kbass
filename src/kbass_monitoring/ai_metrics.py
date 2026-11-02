"""Prometheus metrics for AI-assisted troubleshooting."""

from prometheus_client import Counter


AI_BUDGET_DECISIONS = Counter(
    "cloudops_ai_budget_decisions_total",
    "AI inference budget decisions by outcome",
    ["outcome"],
)

# Initialize known outcomes so they appear in /metrics
# even before the first budget decision.
for outcome in ("allowed", "exhausted", "unavailable"):
    AI_BUDGET_DECISIONS.labels(outcome=outcome)


def record_ai_budget_decision(outcome):
    """Record one AI inference budget decision."""
    if outcome not in ("allowed", "exhausted", "unavailable"):
        raise ValueError("Invalid AI budget outcome")

    AI_BUDGET_DECISIONS.labels(outcome=outcome).inc()
