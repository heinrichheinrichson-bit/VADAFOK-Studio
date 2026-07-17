"""Lightweight diagnostics for Template Editor refresh gateways.

Profiling is disabled by default. When enabled, the profiler records call
counts, elapsed time and bounded refresh-chain events without changing refresh
behavior or swallowing errors. All diagnostics remain in memory and are
detached from the normal application UI.
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


@dataclass
class RefreshEvent:
    """One completed gateway call in a nested refresh chain."""

    sequence: int
    name: str
    parent_sequence: int | None
    root_sequence: int
    depth: int
    started_seconds: float
    elapsed_seconds: float
    failed: bool = False

    def snapshot(self) -> dict[str, int | float | str | bool | None]:
        return {
            "sequence": self.sequence,
            "name": self.name,
            "parent_sequence": self.parent_sequence,
            "root_sequence": self.root_sequence,
            "depth": self.depth,
            "started_seconds": self.started_seconds,
            "elapsed_seconds": self.elapsed_seconds,
            "failed": self.failed,
        }


@dataclass
class _ActiveRefresh:
    sequence: int
    name: str
    parent_sequence: int | None
    root_sequence: int
    depth: int
    started_seconds: float


class TemplateRefreshProfiler:
    """Collect optional, in-memory refresh diagnostics."""

    def __init__(
        self,
        *,
        enabled: bool = False,
        event_limit: int = 1000,
    ) -> None:
        self.enabled = bool(enabled)
        self.event_limit = max(1, int(event_limit))
        self._metrics: dict[str, RefreshMetric] = {}
        self._events: list[RefreshEvent] = []
        self._active: list[_ActiveRefresh] = []
        self._next_sequence = 1
        self._dropped_events = 0

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = bool(enabled)

    def run(self, name: str, callback: Callable[[], _Result]) -> _Result:
        """Run *callback* and collect diagnostics only when profiling is enabled."""

        if not self.enabled:
            return callback()

        sequence = self._next_sequence
        self._next_sequence += 1
        parent = self._active[-1] if self._active else None
        started = perf_counter()
        active = _ActiveRefresh(
            sequence=sequence,
            name=name,
            parent_sequence=parent.sequence if parent else None,
            root_sequence=parent.root_sequence if parent else sequence,
            depth=len(self._active),
            started_seconds=started,
        )
        self._active.append(active)
        failed = False
        try:
            return callback()
        except BaseException:
            failed = True
            raise
        finally:
            elapsed = perf_counter() - started
            self._metrics.setdefault(name, RefreshMetric()).record(elapsed)
            self._active.pop()
            self._append_event(
                RefreshEvent(
                    sequence=active.sequence,
                    name=active.name,
                    parent_sequence=active.parent_sequence,
                    root_sequence=active.root_sequence,
                    depth=active.depth,
                    started_seconds=active.started_seconds,
                    elapsed_seconds=elapsed,
                    failed=failed,
                )
            )

    def _append_event(self, event: RefreshEvent) -> None:
        if len(self._events) >= self.event_limit:
            self._events.pop(0)
            self._dropped_events += 1
        self._events.append(event)

    def reset(self) -> None:
        """Clear metrics and analysis data without changing enabled state."""

        self._metrics.clear()
        self.reset_analysis()

    def reset_analysis(self) -> None:
        """Clear recorded events while preserving aggregate timing metrics."""

        self._events.clear()
        self._active.clear()
        self._next_sequence = 1
        self._dropped_events = 0

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

    def analysis_snapshot(self) -> dict[str, Any]:
        """Return ordered events, counts and reconstructed top-level chains."""

        ordered_events = sorted(self._events, key=lambda event: event.sequence)
        event_snapshots = [event.snapshot() for event in ordered_events]
        counts: dict[str, int] = {}
        for event in ordered_events:
            counts[event.name] = counts.get(event.name, 0) + 1

        chains: list[dict[str, Any]] = []
        events_by_root: dict[int, list[RefreshEvent]] = {}
        for event in ordered_events:
            events_by_root.setdefault(event.root_sequence, []).append(event)

        for root_sequence in sorted(events_by_root):
            chain_events = events_by_root[root_sequence]
            root = next(
                (event for event in chain_events if event.sequence == root_sequence),
                chain_events[0],
            )
            chains.append(
                {
                    "root_sequence": root_sequence,
                    "name": root.name,
                    "elapsed_seconds": root.elapsed_seconds,
                    "failed": root.failed,
                    "events": [event.snapshot() for event in chain_events],
                }
            )

        return {
            "enabled": self.enabled,
            "event_limit": self.event_limit,
            "dropped_events": self._dropped_events,
            "total_events": len(event_snapshots),
            "counts": dict(sorted(counts.items())),
            "events": event_snapshots,
            "chains": chains,
        }

    def analysis_text(self) -> str:
        """Return a compact, deterministic text representation of refresh chains."""

        analysis = self.analysis_snapshot()
        status = "AKTIV" if analysis["enabled"] else "INAKTIV"
        lines = [
            "=== Refresh Analysis ===",
            f"Status: {status}",
            f"Ereignisse: {analysis['total_events']}",
            f"Ketten: {len(analysis['chains'])}",
        ]
        if analysis["dropped_events"]:
            lines.append(f"Verworfene ältere Ereignisse: {analysis['dropped_events']}")

        if not analysis["chains"]:
            lines.append("Keine Analyseereignisse vorhanden.")
            return "\n".join(lines)

        for chain in analysis["chains"]:
            suffix = " [FEHLER]" if chain["failed"] else ""
            lines.append("")
            lines.append(
                f"{chain['name']} #{chain['root_sequence']}"
                f" ({chain['elapsed_seconds'] * 1000.0:.3f} ms){suffix}"
            )
            for event in chain["events"]:
                marker = " !FEHLER" if event["failed"] else ""
                lines.append(
                    f"{'  ' * event['depth']}- {event['name']} "
                    f"({event['elapsed_seconds'] * 1000.0:.3f} ms){marker}"
                )
        return "\n".join(lines)

    def chain_analysis_snapshot(self) -> dict[str, Any]:
        """Aggregate identical refresh-chain structures without changing runtime."""

        analysis = self.analysis_snapshot()
        grouped: dict[tuple[tuple[int, str], ...], dict[str, Any]] = {}

        for chain in analysis["chains"]:
            events = chain["events"]
            if not events:
                continue

            base_depth = min(int(event["depth"]) for event in events)
            structure = tuple(
                (int(event["depth"]) - base_depth, str(event["name"]))
                for event in events
            )
            signature = ">".join(
                f"{depth}:{name}" for depth, name in structure
            )
            elapsed_seconds = float(chain["elapsed_seconds"])

            group = grouped.setdefault(
                structure,
                {
                    "signature": signature,
                    "name": str(chain["name"]),
                    "count": 0,
                    "total_seconds": 0.0,
                    "minimum_seconds": elapsed_seconds,
                    "maximum_seconds": elapsed_seconds,
                    "failed_count": 0,
                    "gateways": [name for _, name in structure],
                    "structure": [
                        {"depth": depth, "name": name}
                        for depth, name in structure
                    ],
                },
            )
            group["count"] += 1
            group["total_seconds"] += elapsed_seconds
            group["minimum_seconds"] = min(
                group["minimum_seconds"],
                elapsed_seconds,
            )
            group["maximum_seconds"] = max(
                group["maximum_seconds"],
                elapsed_seconds,
            )
            if chain["failed"]:
                group["failed_count"] += 1

        groups: list[dict[str, Any]] = []
        for group in grouped.values():
            count = group["count"]
            group["average_seconds"] = (
                group["total_seconds"] / count if count else 0.0
            )
            groups.append(group)

        groups.sort(
            key=lambda group: (
                -group["count"],
                -group["total_seconds"],
                group["signature"],
            )
        )

        return {
            "enabled": analysis["enabled"],
            "event_limit": analysis["event_limit"],
            "dropped_events": analysis["dropped_events"],
            "total_events": analysis["total_events"],
            "total_chains": len(analysis["chains"]),
            "unique_chains": len(groups),
            "chains": groups,
        }

    def chain_analysis_text(self) -> str:
        """Return grouped refresh-chain statistics as deterministic plain text."""

        analysis = self.chain_analysis_snapshot()
        status = "AKTIV" if analysis["enabled"] else "INAKTIV"
        lines = [
            "=== Refresh Chain Analysis ===",
            f"Status: {status}",
            f"Ketten gesamt: {analysis['total_chains']}",
            f"Eindeutige Ketten: {analysis['unique_chains']}",
        ]
        if analysis["dropped_events"]:
            lines.append(f"Verworfene ältere Ereignisse: {analysis['dropped_events']}")

        if not analysis["chains"]:
            lines.append("Keine Refresh-Ketten vorhanden.")
            return "\n".join(lines)

        for index, chain in enumerate(analysis["chains"], start=1):
            lines.append("")
            lines.append(
                f"{index}. {chain['name']} | {chain['count']}x | "
                f"Ø {chain['average_seconds'] * 1000.0:.3f} ms | "
                f"min {chain['minimum_seconds'] * 1000.0:.3f} ms | "
                f"max {chain['maximum_seconds'] * 1000.0:.3f} ms"
            )
            if chain["failed_count"]:
                lines.append(f"   Fehler: {chain['failed_count']}")
            for event in chain["structure"]:
                lines.append(
                    f"{'  ' * (event['depth'] + 1)}- {event['name']}"
                )

        return "\n".join(lines)

    def hotspot_analysis_snapshot(self) -> dict[str, Any]:
        """Rank gateway metrics by frequency and elapsed time."""

        snapshot = self.snapshot()
        metrics = snapshot["metrics"]
        total_count = sum(int(metric["count"]) for metric in metrics.values())
        total_seconds = sum(
            float(metric["total_seconds"]) for metric in metrics.values()
        )

        gateways: list[dict[str, Any]] = []
        for name, metric in metrics.items():
            count = int(metric["count"])
            gateway_total = float(metric["total_seconds"])
            gateway = {
                "name": name,
                "count": count,
                "total_seconds": gateway_total,
                "average_seconds": float(metric["average_seconds"]),
                "last_seconds": float(metric["last_seconds"]),
                "maximum_seconds": float(metric["maximum_seconds"]),
                "count_share": count / total_count if total_count else 0.0,
                "time_share": (
                    gateway_total / total_seconds if total_seconds else 0.0
                ),
            }
            gateways.append(gateway)

        by_total_time = sorted(
            gateways,
            key=lambda gateway: (
                -gateway["total_seconds"],
                -gateway["count"],
                gateway["name"],
            ),
        )
        by_count = sorted(
            gateways,
            key=lambda gateway: (
                -gateway["count"],
                -gateway["total_seconds"],
                gateway["name"],
            ),
        )
        by_average_time = sorted(
            gateways,
            key=lambda gateway: (
                -gateway["average_seconds"],
                -gateway["count"],
                gateway["name"],
            ),
        )
        by_maximum_time = sorted(
            gateways,
            key=lambda gateway: (
                -gateway["maximum_seconds"],
                -gateway["count"],
                gateway["name"],
            ),
        )

        return {
            "enabled": snapshot["enabled"],
            "total_count": total_count,
            "total_seconds": total_seconds,
            "gateway_count": len(gateways),
            "gateways": [dict(gateway) for gateway in by_total_time],
            "rankings": {
                "by_total_time": [dict(gateway) for gateway in by_total_time],
                "by_count": [dict(gateway) for gateway in by_count],
                "by_average_time": [
                    dict(gateway) for gateway in by_average_time
                ],
                "by_maximum_time": [
                    dict(gateway) for gateway in by_maximum_time
                ],
            },
        }


    def pattern_analysis_snapshot(self) -> dict[str, Any]:
        """Analyze recurring parent-child transitions in recorded refresh chains."""

        analysis = self.analysis_snapshot()
        transition_counts: dict[tuple[str, str], int] = {}
        outgoing_counts: dict[str, int] = {}
        incoming_counts: dict[str, int] = {}

        for chain in analysis["chains"]:
            events = chain["events"]
            events_by_sequence = {
                int(event["sequence"]): event
                for event in events
            }
            for event in events:
                parent_sequence = event["parent_sequence"]
                if parent_sequence is None:
                    continue
                parent = events_by_sequence.get(int(parent_sequence))
                if parent is None:
                    continue

                source = str(parent["name"])
                target = str(event["name"])
                key = (source, target)
                transition_counts[key] = transition_counts.get(key, 0) + 1
                outgoing_counts[source] = outgoing_counts.get(source, 0) + 1
                incoming_counts[target] = incoming_counts.get(target, 0) + 1

        transitions: list[dict[str, Any]] = []
        for (source, target), count in transition_counts.items():
            outgoing_total = outgoing_counts[source]
            target_share = count / outgoing_total if outgoing_total else 0.0
            transitions.append(
                {
                    "source": source,
                    "target": target,
                    "signature": f"{source}>{target}",
                    "count": count,
                    "source_total": outgoing_total,
                    "target_share": target_share,
                }
            )

        transitions.sort(
            key=lambda transition: (
                -transition["count"],
                transition["source"],
                transition["target"],
            )
        )

        source_summaries: list[dict[str, Any]] = []
        for source in sorted(outgoing_counts):
            source_transitions = [
                dict(transition)
                for transition in transitions
                if transition["source"] == source
            ]
            source_summaries.append(
                {
                    "name": source,
                    "outgoing_count": outgoing_counts[source],
                    "unique_targets": len(source_transitions),
                    "transitions": source_transitions,
                }
            )

        source_summaries.sort(
            key=lambda source: (
                -source["outgoing_count"],
                source["name"],
            )
        )

        return {
            "enabled": analysis["enabled"],
            "event_limit": analysis["event_limit"],
            "dropped_events": analysis["dropped_events"],
            "total_events": analysis["total_events"],
            "total_chains": len(analysis["chains"]),
            "total_transitions": sum(transition_counts.values()),
            "unique_transitions": len(transitions),
            "transitions": transitions,
            "sources": source_summaries,
            "incoming_counts": dict(sorted(incoming_counts.items())),
        }

    def pattern_analysis_text(self) -> str:
        """Return recurring refresh transitions as deterministic plain text."""

        analysis = self.pattern_analysis_snapshot()
        status = "AKTIV" if analysis["enabled"] else "INAKTIV"
        lines = [
            "=== Refresh Pattern Analysis ===",
            f"Status: {status}",
            f"Ketten: {analysis['total_chains']}",
            f"Übergänge gesamt: {analysis['total_transitions']}",
            f"Eindeutige Übergänge: {analysis['unique_transitions']}",
        ]
        if analysis["dropped_events"]:
            lines.append(f"Verworfene ältere Ereignisse: {analysis['dropped_events']}")

        if not analysis["transitions"]:
            lines.append("Keine Refresh-Übergänge vorhanden.")
            return "\n".join(lines)

        lines.append("")
        lines.append("Übergänge:")
        for index, transition in enumerate(analysis["transitions"], start=1):
            lines.append(
                f"{index}. {transition['source']} -> {transition['target']} | "
                f"{transition['count']}x | "
                f"{transition['target_share'] * 100.0:.2f}% der Ausgänge"
            )

        return "\n".join(lines)

    def hotspot_analysis_text(self) -> str:
        """Return a deterministic gateway-hotspot report."""

        analysis = self.hotspot_analysis_snapshot()
        status = "AKTIV" if analysis["enabled"] else "INAKTIV"
        lines = [
            "=== Refresh Hotspot Analysis ===",
            f"Status: {status}",
            f"Gateways: {analysis['gateway_count']}",
            f"Aufrufe gesamt: {analysis['total_count']}",
            f"Gateway-Zeit gesamt: {analysis['total_seconds'] * 1000.0:.3f} ms",
        ]

        if not analysis["gateways"]:
            lines.append("Keine Gateway-Messwerte vorhanden.")
            return "\n".join(lines)

        lines.append("")
        lines.append("Ranking nach Gesamtzeit:")
        for index, gateway in enumerate(
            analysis["rankings"]["by_total_time"],
            start=1,
        ):
            lines.append(
                f"{index}. {gateway['name']} | "
                f"{gateway['count']}x | "
                f"{gateway['total_seconds'] * 1000.0:.3f} ms gesamt | "
                f"Ø {gateway['average_seconds'] * 1000.0:.3f} ms | "
                f"{gateway['time_share'] * 100.0:.2f}% Zeit"
            )

        lines.append("")
        lines.append(
            "Häufigster Gateway: "
            f"{analysis['rankings']['by_count'][0]['name']}"
        )
        lines.append(
            "Höchster Durchschnitt: "
            f"{analysis['rankings']['by_average_time'][0]['name']}"
        )
        lines.append(
            "Höchster Einzelwert: "
            f"{analysis['rankings']['by_maximum_time'][0]['name']}"
        )
        return "\n".join(lines)
