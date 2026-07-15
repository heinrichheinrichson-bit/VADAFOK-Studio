"""Persistent window geometry for VADAFOK Studio.

The manager is intentionally small and independent from the UI framework. It
stores only window geometry/state in ``data/workspace_state.json`` and never
changes a user's chosen minimum/maximum size.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

_STATE_PATH = Path(__file__).resolve().parent.parent / "data" / "workspace_state.json"


def _load() -> dict[str, dict[str, Any]]:
    try:
        if _STATE_PATH.exists():
            data = json.loads(_STATE_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
    except Exception:
        pass
    return {}


def _save(data: dict[str, dict[str, Any]]) -> None:
    try:
        _STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = _STATE_PATH.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        tmp.replace(_STATE_PATH)
    except Exception as exc:
        print(f"[Workspace State] save failed: {exc}")


def _valid_geometry(value: Any) -> str | None:
    if not isinstance(value, str) or "x" not in value:
        return None
    # Tk geometry may be ``WxH+X+Y`` or ``WxH-X-Y``. Let Tk perform the final
    # validation; this lightweight check only rejects obviously bad values.
    head = value.split("+", 1)[0].split("-", 1)[0]
    parts = head.split("x", 1)
    if len(parts) != 2:
        return None
    try:
        if int(parts[0]) < 100 or int(parts[1]) < 80:
            return None
    except ValueError:
        return None
    return value


def restore_window(window: Any, key: str) -> bool:
    """Restore a previously saved geometry and maximized state."""
    record = _load().get(key, {})
    geometry = _valid_geometry(record.get("geometry"))
    restored = False
    if geometry:
        try:
            window.geometry(geometry)
            restored = True
        except Exception:
            pass

    if record.get("state") == "zoomed":
        try:
            # Delay until Tk has created the native window.
            window.after(20, lambda: window.state("zoomed"))
            restored = True
        except Exception:
            pass
    return restored


def save_window(window: Any, key: str) -> None:
    """Persist current geometry/state without imposing a minimum size."""
    try:
        if not window.winfo_exists():
            return
    except Exception:
        return

    try:
        state = str(window.state())
    except Exception:
        state = "normal"

    data = _load()
    current = data.get(key, {}) if isinstance(data.get(key), dict) else {}

    # When maximized, ``geometry()`` can report the maximized rectangle. Keep
    # the last normal geometry and additionally remember the zoomed state.
    if state != "zoomed":
        try:
            geometry = _valid_geometry(str(window.geometry()))
            if geometry:
                current["geometry"] = geometry
        except Exception:
            pass
    current["state"] = "zoomed" if state == "zoomed" else "normal"
    data[key] = current
    _save(data)


def watch_window(window: Any, key: str, delay_ms: int = 350) -> None:
    """Debounce Configure events and continuously persist user resizing."""
    timer_attr = f"_vadafok_workspace_timer_{key.replace('-', '_')}"

    def schedule(_event: Any = None) -> None:
        try:
            previous = getattr(window, timer_attr, None)
            if previous is not None:
                window.after_cancel(previous)
            timer = window.after(delay_ms, lambda: save_window(window, key))
            setattr(window, timer_attr, timer)
        except Exception:
            pass

    try:
        window.bind("<Configure>", schedule, add="+")
    except Exception:
        pass
