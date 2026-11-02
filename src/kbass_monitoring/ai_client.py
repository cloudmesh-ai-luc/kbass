"""Optional read-only AI analysis for monitoring incidents."""

import os

from .providers import get_provider


def analyze_with_ai(incident):
    """Request structured diagnostic guidance from a configured LLM."""
    provider_name = os.environ.get(
        "CLOUDOPS_AI_PROVIDER", "openai"
    ).lower()

    provider = get_provider(provider_name)
    return provider.analyze(incident)
