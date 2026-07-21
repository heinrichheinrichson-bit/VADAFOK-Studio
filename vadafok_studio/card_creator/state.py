"""State models owned by the Card Creator feature."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class CardCreatorState:
    """Non-widget Card Creator state, introduced incrementally."""

    batch_items: list[dict[str, Any]] = field(default_factory=list)
    batch_selected_index: int | None = None
