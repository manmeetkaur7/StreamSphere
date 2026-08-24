from __future__ import annotations

from collections import Counter
from threading import Lock


class MetricsRegistry:
    def __init__(self) -> None:
        self._lock = Lock()
        self._counters: Counter[str] = Counter()
        self._timings: Counter[str] = Counter()

    def increment(self, name: str, value: int = 1) -> None:
        with self._lock:
            self._counters[name] += value

    def observe_latency(self, milliseconds: float) -> None:
        with self._lock:
            self._counters["http.requests.total"] += 1
            self._timings["http.requests.duration_ms.total"] += round(milliseconds, 2)

    def snapshot(self) -> dict[str, float | int]:
        with self._lock:
            average_latency = 0.0
            total_requests = self._counters.get("http.requests.total", 0)
            if total_requests:
                average_latency = round(
                    self._timings.get("http.requests.duration_ms.total", 0.0) / total_requests,
                    2,
                )
            payload = dict(self._counters)
            payload["http.requests.duration_ms.avg"] = average_latency
            return payload


_metrics_registry = MetricsRegistry()


def get_metrics_registry() -> MetricsRegistry:
    return _metrics_registry
