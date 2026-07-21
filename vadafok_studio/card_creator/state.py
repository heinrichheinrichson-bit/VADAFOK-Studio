"""State models owned by the Card Creator feature."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CardCreatorState:
    """Non-widget Card Creator state, introduced incrementally."""

    batch_items: list[dict[str, Any]] = field(default_factory=list)
    batch_selected_index: int | None = None
    preview_background_cache: Any = None
    preview_background_key: tuple[str, int] | None = None
    last_render: Path | None = None
    data_undo_stack: list[dict[str, str]] = field(default_factory=list)
    data_redo_stack: list[dict[str, str]] = field(default_factory=list)
    history_limit: int = 50
