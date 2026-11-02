"""Redis-backed, application-wide sliding-window AI inference budget."""

import logging
import uuid

from redis import Redis
from redis.exceptions import RedisError

logger = logging.getLogger(__name__)


_ACQUIRE_SCRIPT = """
local key = KEYS[1]
local limit = tonumber(ARGV[1])
local window_ms = tonumber(ARGV[2])
local member = ARGV[3]

local now = redis.call('TIME')
local now_ms = now[1] * 1000 + math.floor(now[2] / 1000)

redis.call('ZREMRANGEBYSCORE', key, '-inf', now_ms - window_ms)

if redis.call('ZCARD', key) >= limit then
    return 0
end

redis.call('ZADD', key, now_ms, member)
redis.call('PEXPIRE', key, window_ms)

return 1
"""


class RedisInferenceBudget:
    """Enforce one inference budget across all application workers."""

    def __init__(
        self,
        redis_url,
        max_requests=10,
        window_seconds=60,
        key="cloudops:ai:inference_budget",
    ):
        if max_requests <= 0 or window_seconds <= 0:
            raise ValueError("Budget limits must be positive")

        if not redis_url:
            raise ValueError("Redis URL is required")

        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key = key
        self.client = Redis.from_url(
            redis_url,
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        self._acquire = self.client.register_script(_ACQUIRE_SCRIPT)

    def try_acquire(self):
        """Atomically reserve an inference attempt, failing closed on errors."""
        try:
            return bool(
                self._acquire(
                    keys=[self.key],
                    args=[
                        self.max_requests,
                        int(self.window_seconds * 1000),
                        uuid.uuid4().hex,
                    ],
                )
            )
        except RedisError:
            logger.warning("redis_ai_budget_unavailable")
            return False
