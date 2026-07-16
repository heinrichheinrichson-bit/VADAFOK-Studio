"""Controller for Template Editor selection workflows."""

from __future__ import annotations

from typing import Any, Callable, Iterable


class TemplateEditorController:
    """Coordinate Template Editor state without owning GUI widgets."""

    def __init__(
        self,
        app: Any,
        list_templates: Callable[[], Iterable[str]],
        load_template: Callable[[str], dict],
    ) -> None:
        self.app = app
        self._list_templates = list_templates
        self._load_template = load_template

    def available_templates(self) -> list[str]:
        return list(self._list_templates())

    def select_template(self, name: str) -> bool:
        available = self.available_templates()
        if name not in available:
            return False

        self.app.template_collapsed_groups = set()
        self.app.template_selected_name = name
        self.app.template_selected_field = None
        self.app.template_selected_fields = set()
        self.app.template_working_data = self._load_template(name)
        self.app.show_template_editor_page()
        return True
