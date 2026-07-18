"""Simple in-memory sliding-window rate limiter."""

import time
from collections import defaultdict, deque


class RateLimiter:
    def __init__(self, max_per_minute: int = 10) -> None:
        self.max_per_minute = max_per_minute
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> bool:
        now = time.monotonic()
        window = self._hits[key]
        while window and now - window[0] > 60:
            window.popleft()
        if len(window) >= self.max_per_minute:
            return False
        window.append(now)
        return True


rate_limiter = RateLimiter()
