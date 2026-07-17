"""Lightweight diagnostics for Template Editor refresh gateways.

Profiling is disabled by default. When enabled, the profiler records call
counts and elapsed time without changing refresh behavior or swallowing errors.
The developer view is a detached, text-only representation; it does not create
widgets or modify the normal application UI.
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

    def developer_snapshot(self) -> dict[str, Any]:
        """Return a detached summary tailored for diagnostics consumers."""

        snapshot = self.snapshot()
        metrics = snapshot["metrics"]
        total_count = sum(metric["count"] for metric in metrics.values())
        total_seconds = sum(metric["total_seconds"] for metric in metrics.values())
        maximum_seconds = max(
            (metric["maximum_seconds"] for metric in metrics.values()),
            default=0.0,
        )
        average_seconds = total_seconds / total_count if total_count else 0.0

        return {
            "enabled": snapshot["enabled"],
            "total_count": total_count,
            "total_seconds": total_seconds,
            "average_seconds": average_seconds,
            "maximum_seconds": maximum_seconds,
            "metrics": metrics,
        }

    def developer_text(self) -> str:
        """Return a stable, human-readable developer view."""

        view = self.developer_snapshot()
        status = "AKTIV" if view["enabled"] else "INAKTIV"
        lines = [
            f"RefreshProfiler: {status}",
            f"Gesamt: {view['total_count']} Refreshes",
            f"Gesamtzeit: {view['total_seconds'] * 1000.0:.3f} ms",
            f"Durchschnitt: {view['average_seconds'] * 1000.0:.3f} ms",
            f"Maximum: {view['maximum_seconds'] * 1000.0:.3f} ms",
        ]

        if not view["metrics"]:
            lines.append("Keine Messwerte vorhanden.")
            return "\n".join(lines)

        lines.append("Gateways:")
        for name, metric in view["metrics"].items():
            lines.append(
                "  "
                f"{name}: {metric['count']} | "
                f"Ø {metric['average_seconds'] * 1000.0:.3f} ms | "
                f"max {metric['maximum_seconds'] * 1000.0:.3f} ms"
            )
        return "\n".join(lines)
