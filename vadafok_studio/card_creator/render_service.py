"""Card Creator background resolution and rendering services."""

from __future__ import annotations

from typing import Any


class CardRenderService:
    def __init__(
        self,
        app: Any,
        load_template,
        background_path,
        template_dir,
    ) -> None:
        self.app = app
        self._load_template = load_template
        self._background_path = background_path
        self._template_dir = template_dir

    def resolve_background_path(self) -> str:
        template_name = self.app.card_selected_template.get()
        if not template_name:
            return ""

        template = self._load_template(template_name)
        configured = self._background_path(template_name, template)
        if configured.exists():
            return str(configured)

        folder = self._template_dir(template_name)
        for filename in (
            "background.png",
            "background.jpg",
            "background.jpeg",
            "background.webp",
        ):
            candidate = folder / filename
            if candidate.exists():
                return str(candidate)

        for pattern in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
            matches = list(folder.glob(pattern))
            if matches:
                return str(matches[0])
        return ""
