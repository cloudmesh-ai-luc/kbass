"""Thread-safe, bounded, in-memory cache for AI diagnoses."""

import copy
import threading
import time
from collections import OrderedDict


class DiagnosisCache:
    def __init__(self, ttl_seconds=900, max_entries=100):
        if ttl_seconds <= 0 or max_entries <= 0:
            raise ValueError("Cache limits must be positive")

        self.ttl_seconds = ttl_seconds
        self.max_entries = max_entries
        self._entries = OrderedDict()
        self._lock = threading.RLock()
        self._inflight_locks = {}

    def get(self, key):
        with self._lock:
            entry = self._entries.get(key)
            if entry is None:
                return None

            expires_at, value = entry

            if time.monotonic() >= expires_at:
                del self._entries[key]
                return None

            self._entries.move_to_end(key)
            return copy.deepcopy(value)

    def set(self, key, value):
        with self._lock:
            now = time.monotonic()

            for existing_key, (expires_at, _) in list(
                self._entries.items()
            ):
                if now >= expires_at:
                    del self._entries[existing_key]

            self._entries[key] = (
                now + self.ttl_seconds,
                copy.deepcopy(value),
            )
            self._entries.move_to_end(key)

            while len(self._entries) > self.max_entries:
                self._entries.popitem(last=False)

    def clear(self):
        with self._lock:
            self._entries.clear()


    def acquire_inference_lock(self, key):
        """Return a context manager that serializes inference for one key."""
        from contextlib import contextmanager

        @contextmanager
        def locked():
            with self._lock:
                entry = self._inflight_locks.get(key)
                if entry is None:
                    entry = [threading.Lock(), 0]
                    self._inflight_locks[key] = entry
                entry[1] += 1
                inference_lock = entry[0]

            try:
                with inference_lock:
                    yield
            finally:
                with self._lock:
                    entry[1] -= 1
                    if entry[1] == 0:
                        del self._inflight_locks[key]

        return locked()
