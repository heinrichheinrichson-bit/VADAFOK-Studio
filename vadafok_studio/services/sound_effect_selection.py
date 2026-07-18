"""Pure helpers for portable Live Card sound-effect selection."""
from __future__ import annotations

from pathlib import Path
from typing import Any


def effect_display_name(relative_path: Any) -> str:
    value = str(relative_path or "").strip()
    if not value:
        return "Kein Effekt ausgewählt"
    return Path(value).name


def portable_effect_path(service: Any, selected_path: Any) -> str | None:
    """Return a POSIX path relative to the service's Sounds directory."""
    resolved = service.resolve(selected_path)
    sounds_dir = service.sounds_dir
    if resolved is None or sounds_dir is None or not service.exists(resolved):
        return None
    try:
        return resolved.relative_to(sounds_dir.resolve(strict=False)).as_posix()
    except (OSError, RuntimeError, ValueError):
        return None
