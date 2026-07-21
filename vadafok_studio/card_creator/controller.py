"""Controller for Card Creator template-selection workflows.

This first extraction step intentionally covers only the stable template-list,
recent-history and selection-refresh orchestration. Rendering and form-building
remain on the application during this version.
"""

from __future__ import annotations

from typing import Any, Callable, Iterable

from vadafok_studio.core.recent_templates import (
    load_recent_templates,
    record_recent_template,
    remove_recent_template,
)
from .state import CardCreatorState


class CardCreatorController:
    """Coordinate Card Creator template state without owning GUI widgets."""

    def __init__(
        self,
        app: Any,
        list_templates: Callable[[], Iterable[str]],
        state: CardCreatorState | None = None,
    ) -> None:
        self.app = app
        self.state = state or app.card_creator_state
        self._list_templates = list_templates

    def available_templates(self) -> list[str]:
        return list(self._list_templates())

    def load_recent(self) -> list[str]:
        recent = load_recent_templates(self.available_templates())
        self.app.card_recent_templates = recent
        return recent

    def remove_recent(self, name: str) -> list[str]:
        recent = remove_recent_template(name, self.available_templates())
        self.app.card_recent_templates = recent
        self.app.card_refresh_recent_templates()
        return recent

    def select_template(self, name: str) -> bool:
        available = self.available_templates()
        if name not in available:
            return False

        self.app.card_recent_templates = record_recent_template(name, available)
        self.app.card_selected_template.set(name)
        self.app.card_output_name.set(self.app.card_default_output_name())
        self.app.card_data_undo_stack = []
        self.app.card_data_redo_stack = []
        self.app.card_creator_preview_image = None
        self.state.preview_background_cache = None
        self.state.preview_background_key = None
        self.state.last_render = None

        self.app.card_refresh_recent_templates()
        self.app.card_refresh_all_templates()
        self.app.card_build_form()
        self.app.card_update_preview()
        return True
