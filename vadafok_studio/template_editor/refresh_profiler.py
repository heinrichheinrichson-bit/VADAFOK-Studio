"""Lightweight diagnostics for Template Editor refresh gateways.

Profiling is disabled by default.  When enabled, the profiler records call
counts and elapsed time without changing refresh behavior or swallowing errors.
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any, Callable, TypeVar


_Result = TypeVar("_Result")


@dataclass
class RefreshMetric:
    """Aggregated timing information for one refresh gateway."""

    count: int = 0
    total_seconds: float = 0.0
    last_seconds: float = 0.0
    maximum_seconds: float = 0.0

    def record(self, elapsed_seconds: float) -> None:
        self.count += 1
        self.total_seconds += elapsed_seconds
        self.last_seconds = elapsed_seconds
        self.maximum_seconds = max(self.maximum_seconds, elapsed_seconds)

    def snapshot(self) -> dict[str, int | float]:
        average = self.total_seconds / self.count if self.count else 0.0
        return {
            "count": self.count,
            "total_seconds": self.total_seconds,
            "last_seconds": self.last_seconds,
            "maximum_seconds": self.maximum_seconds,
            "average_seconds": average,
        }


class TemplateRefreshProfiler:
    """Collect optional, in-memory refresh diagnostics."""

    def __init__(self, *, enabled: bool = False) -> None:
        self.enabled = bool(enabled)
        self._metrics: dict[str, RefreshMetric] = {}

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = bool(enabled)

    def run(self, name: str, callback: Callable[[], _Result]) -> _Result:
        """Run *callback* and record its duration only when profiling is enabled."""
        if not self.enabled:
            return callback()

        started = perf_counter()
        try:
            return callback()
        finally:
            elapsed = perf_counter() - started
            self._metrics.setdefault(name, RefreshMetric()).record(elapsed)

    def reset(self) -> None:
        self._metrics.clear()

    def snapshot(self) -> dict[str, Any]:
        return {
            "enabled": self.enabled,
            "metrics": {
                name: metric.snapshot()
                for name, metric in sorted(self._metrics.items())
            },
        }
