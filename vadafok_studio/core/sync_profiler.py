"""Lightweight high-resolution timing profiler for SHOW diagnostics."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path
import threading
import time
from typing import Iterable

from .config import APP_ROOT


class SyncProfiler:
    """Collect relative timing marks and append them to a diagnostic log.

    The profiler is deliberately best-effort: logging failures must never
    interrupt a Live Card SHOW action.
    """

    _write_lock = threading.Lock()

    def __init__(
        self,
        enabled: bool = False,
        session_name: str = "LiveCard SHOW",
        log_path: str | Path | None = None,
    ) -> None:
        self.enabled = bool(enabled)
        self.session_name = str(session_name or "Sync session")
        self.log_path = Path(log_path) if log_path else APP_ROOT / "logs" / "sync_profile.log"
        self.started_at = time.perf_counter()
        self.created_at = datetime.now()
        self._marks: list[tuple[float, str]] = []
        self._saved = False

    def mark(self, name: str) -> float | None:
        """Record a named mark and return its elapsed seconds."""
        if not self.enabled:
            return None
        elapsed = time.perf_counter() - self.started_at
        self._marks.append((elapsed, str(name or "mark")))
        return elapsed

    @property
    def marks(self) -> tuple[tuple[float, str], ...]:
        return tuple(self._marks)

    def _render(self) -> str:
        width = 72
        lines = [
            "=" * width,
            self.session_name,
            self.created_at.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3],
            "",
        ]
        for elapsed, name in self._marks:
            lines.append(f"{elapsed:0.6f}  {name}")
        lines.extend(("=" * width, ""))
        return "\n".join(lines)

    def save(self) -> bool:
        """Append the current session once. Never raise into production code."""
        if not self.enabled or self._saved:
            return False
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            payload = self._render()
            with self._write_lock:
                with self.log_path.open("a", encoding="utf-8", newline="\n") as handle:
                    handle.write(payload)
            self._saved = True
            return True
        except Exception:
            return False

    def clear(self) -> None:
        self.started_at = time.perf_counter()
        self.created_at = datetime.now()
        self._marks.clear()
        self._saved = False
