from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta
from threading import Lock


class LoginRateLimiter:
    """Process-local, bounded-window login protection; replace with Redis for multi-instance deployments."""

    def __init__(self) -> None:
        self._failures: dict[str, deque[datetime]] = defaultdict(deque)
        self._blocked_until: dict[str, datetime] = {}
        self._lock = Lock()

    def is_blocked(self, key: str, *, now: datetime, window_seconds: int) -> bool:
        with self._lock:
            blocked_until = self._blocked_until.get(key)
            if blocked_until and blocked_until > now:
                return True
            self._blocked_until.pop(key, None)
            cutoff = now - timedelta(seconds=window_seconds)
            failures = self._failures[key]
            while failures and failures[0] < cutoff:
                failures.popleft()
            return False

    def failure(self, key: str, *, now: datetime, max_attempts: int, cooldown_seconds: int) -> None:
        with self._lock:
            failures = self._failures[key]
            failures.append(now)
            if len(failures) >= max_attempts:
                self._blocked_until[key] = now + timedelta(seconds=cooldown_seconds)

    def success(self, key: str) -> None:
        with self._lock:
            self._failures.pop(key, None)
            self._blocked_until.pop(key, None)

    def clear(self) -> None:
        with self._lock:
            self._failures.clear()
            self._blocked_until.clear()


login_rate_limiter = LoginRateLimiter()


def utc_now() -> datetime:
    return datetime.now(UTC)
