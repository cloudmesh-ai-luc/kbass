"""Thread-safe sliding-window budget for AI inference attempts."""

import threading
import time
from collections import deque


class InferenceBudget:
    """Limit inference attempts within a rolling time window."""

    def __init__(self, max_requests=10, window_seconds=60):
        if max_requests <= 0 or window_seconds <= 0:
            raise ValueError("Budget limits must be positive")

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._attempts = deque()
        self._lock = threading.Lock()

    def try_acquire(self):
        """Reserve one inference attempt if the budget permits."""
        with self._lock:
            now = time.monotonic()
            cutoff = now - self.window_seconds

            while self._attempts and self._attempts[0] <= cutoff:
                self._attempts.popleft()

            if len(self._attempts) >= self.max_requests:
                return False

            self._attempts.append(now)
            return True
