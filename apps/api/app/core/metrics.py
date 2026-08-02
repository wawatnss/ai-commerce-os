"""In-memory metrics collector."""

import statistics
import time
from collections import defaultdict, deque
from threading import Lock


class MetricsCollector:
    """Thread-safe in-memory metrics."""

    def __init__(self, window_size: int = 1000):
        self._counts = defaultdict(int)
        self._durations: defaultdict[str, deque[float]] = defaultdict(lambda: deque(maxlen=window_size))
        self._errors = defaultdict(int)
        self._lock = Lock()

    def record_request(self, path: str, method: str, duration_ms: float, status_code: int) -> None:
        key = f"{method} {path}"
        with self._lock:
            self._counts[key] += 1
            self._durations[key].append(duration_ms)
            if status_code >= 500:
                self._errors[key] += 1

    def get(self) -> dict:
        with self._lock:
            result = {}
            for key in self._counts:
                durations = list(self._durations[key])
                result[key] = {
                    "count": self._counts[key],
                    "errors": self._errors[key],
                    "avg_ms": round(sum(durations) / len(durations), 2) if durations else 0,
                    "p95_ms": round(statistics.quantiles(durations, n=20)[18], 2) if len(durations) >= 5 else 0,
                }
            return result


collector = MetricsCollector()
