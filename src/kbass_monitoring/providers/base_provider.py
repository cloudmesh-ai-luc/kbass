"""Common interface for CloudOps AI diagnostic providers."""

from abc import ABC, abstractmethod
from typing import Any


class BaseLLMProvider(ABC):
    """Interface for providers returning structured incident diagnoses."""

    @abstractmethod
    def analyze(self, incident: dict[str, Any]) -> dict[str, Any]:
        """Return diagnostic guidance for a monitoring incident."""
        raise NotImplementedError
