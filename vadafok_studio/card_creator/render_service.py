"""Card Creator background resolution and rendering services."""

from __future__ import annotations

from typing import Any
from pathlib import Path

from PIL import Image


class CardRenderService:
    def __init__(
        self,
        app: Any,
        load_template,
        background_path,
        template_dir,
        export_dir: Path,
        render_template_card,
        export_engine: Any,
    ) -> None:
        self.app = app
        self._load_template = load_template
        self._background_path = background_path
        self._template_dir = template_dir
        self._export_dir = Path(export_dir)
        self._render_template_card = render_template_card
        self._export_engine = export_engine

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

    def render_to_file(self, final=False, output_dir=None, output_path=None):
        self._export_dir.mkdir(parents=True, exist_ok=True)
        temporary = self._export_dir / "_vadafok_card_temp_profile_source.png"
        self._render_template_card(
            self.app.card_template(),
            self.app.card_values_plain(),
            temporary,
            self.resolve_background_path(),
            size=None,
        )

        output = (
            Path(output_path)
            if output_path is not None
            else self.app.card_output_path(final=final, output_dir=output_dir)
        )
        profile = getattr(self.app, "card_export_profile", None)
        profile_name = profile.get() if profile is not None else "Broadcast PNG"
        image = Image.open(temporary).convert("RGBA")
        self._export_engine.save_with_profile(
            image, output, profile_name
        )
        try:
            temporary.unlink()
        except Exception:
            pass
        return output
