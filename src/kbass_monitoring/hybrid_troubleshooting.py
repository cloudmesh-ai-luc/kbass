"""Hybrid AI-assisted incident troubleshooting with rule-based fallback."""

import json
import os
from contextlib import nullcontext

from .troubleshooting import analyze_incident
from .diagnosis_cache import DiagnosisCache
from .ai_client import analyze_with_ai


def analyze_incident_hybrid(incident, ai_analyzer=None, cache=None, budget=None):
    """Analyze an incident using AI when available, otherwise use rules."""
    fallback = analyze_incident(incident)

    if ai_analyzer is None:
        return fallback

    if ai_analyzer == "configured":
        ai_analyzer = analyze_with_ai

    cache_key = None

    if cache is not None:
        cache_key = json.dumps(
            {
                "provider": os.environ.get(
                    "CLOUDOPS_AI_PROVIDER", "openai"
                ),
                "model": os.environ.get("CLOUDOPS_AI_MODEL"),
                "analyzer": (
                    "configured"
                    if ai_analyzer is analyze_with_ai
                    else id(ai_analyzer)
                ),
                "incident": {
                    key: incident.get(key)
                    for key in (
                        "name",
                        "state",
                        "active_at",
                        "labels",
                        "summary",
                        "description",
                    )
                },
            },
            sort_keys=True,
            default=str,
        )

        cached = cache.get(cache_key)
        if cached is not None:
            return cached

    lock_context = (
        cache.acquire_inference_lock(cache_key)
        if cache is not None
        else nullcontext()
    )

    try:
        with lock_context:
            if cache is not None:
                cached = cache.get(cache_key)
                if cached is not None:
                    return cached

            # Only actual AI inference attempts consume the budget.
            if budget is not None and not budget.try_acquire():
                return fallback

            result = ai_analyzer(incident)

            if not isinstance(result, dict):
                return fallback

            required_fields = (
                "explanation",
                "possible_causes",
                "recommended_actions",
            )

            if not all(result.get(field) for field in required_fields):
                return fallback

            if not isinstance(result["explanation"], str):
                return fallback

            if not all(
                isinstance(result[field], list)
                and all(isinstance(item, str) and item.strip()
                        for item in result[field])
                for field in ("possible_causes", "recommended_actions")
            ):
                return fallback

            diagnosis = {
                "explanation": result["explanation"],
                "possible_causes": result["possible_causes"],
                "recommended_actions": result["recommended_actions"],
                "diagnosis_type": "ai_assisted",
                "root_cause_confirmed": False,
            }

            if cache is not None:
                cache.set(cache_key, diagnosis)

            return diagnosis

    except Exception:
        return fallback
