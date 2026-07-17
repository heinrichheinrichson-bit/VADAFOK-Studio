"""Central refresh gateway for the Template Editor.

The manager deliberately contains no rendering logic.  It provides one stable
interface around the existing application methods so future controller
extractions can happen without changing user-facing behavior.
"""

from __future__ import annotations

from typing import Any


class TemplateRefreshManager:
    """Coordinate targeted Template Editor refresh operations."""

    def __init__(self, app: Any) -> None:
        self.app = app

    def canvas(self, *, refresh_layers: bool = True) -> None:
        self.app.template_draw_canvas(refresh_layers=refresh_layers)

    def overlay(
        self,
        bg_info: dict[str, Any] | None = None,
        *,
        refresh_layers: bool = True,
        refresh_status: bool = True,
    ) -> None:
        self.app.template_update_fields_overlay(
            bg_info=bg_info,
            refresh_layers=refresh_layers,
            refresh_status=refresh_status,
        )

    def layers(self, *, full: bool = False) -> None:
        if not hasattr(self.app, "template_layers_body"):
            return
        if full:
            self.app.template_build_layers_panel()
        else:
            self.app.template_refresh_layers_selection()

    def properties(self, *, load_values: bool = False) -> None:
        if load_values:
            self.app.template_load_selected_properties()
        if hasattr(self.app, "template_props_body"):
            self.app.template_build_properties_panel()

    def selection(self, *, refresh_properties: bool = True) -> None:
        if refresh_properties:
            self.properties(load_values=True)
        self.overlay(refresh_layers=False)
        self.layers(full=False)
