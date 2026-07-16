"""Persistent recent-template history for the Card Creator."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RECENT_TEMPLATES_PATH = DATA_DIR / "card_creator_recent_templates.json"
MAX_RECENT_TEMPLATES = 10


def _clean_names(names: Iterable[object]) -> list[str]:
    cleaned = []
    seen = set()
    for value in names:
        name = str(value or "").strip()
        if not name or name in seen:
            continue
        cleaned.append(name)
        seen.add(name)
    return cleaned


def load_recent_templates(available_templates: Iterable[str] | None = None) -> list[str]:
    try:
        raw = json.loads(RECENT_TEMPLATES_PATH.read_text(encoding="utf-8"))
        names = raw.get("recent_templates", []) if isinstance(raw, dict) else raw
        recent = _clean_names(names)
    except (OSError, ValueError, TypeError):
        recent = []

    if available_templates is not None:
        available = set(_clean_names(available_templates))
        recent = [name for name in recent if name in available]

    return recent[:MAX_RECENT_TEMPLATES]


def save_recent_templates(names: Iterable[str]) -> list[str]:
    recent = _clean_names(names)[:MAX_RECENT_TEMPLATES]
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    temporary = RECENT_TEMPLATES_PATH.with_suffix(".json.tmp")
    temporary.write_text(
        json.dumps({"recent_templates": recent}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    temporary.replace(RECENT_TEMPLATES_PATH)
    return recent


def record_recent_template(
    name: str,
    available_templates: Iterable[str] | None = None,
) -> list[str]:
    normalized_name = str(name or "").strip()
    recent = load_recent_templates(available_templates)

    if not normalized_name:
        return recent

    if available_templates is not None:
        available = set(_clean_names(available_templates))
        if normalized_name not in available:
            return recent

    recent = [item for item in recent if item != normalized_name]
    recent.insert(0, normalized_name)
    return save_recent_templates(recent)


def remove_recent_template(
    name: str,
    available_templates: Iterable[str] | None = None,
) -> list[str]:
    """Remove one item only from the recent history."""
    normalized_name = str(name or "").strip()
    recent = load_recent_templates(available_templates)

    if not normalized_name:
        return recent

    recent = [item for item in recent if item != normalized_name]
    return save_recent_templates(recent)
