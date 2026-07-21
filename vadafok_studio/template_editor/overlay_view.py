"""Field-overlay rendering for the Template Editor canvas."""

from __future__ import annotations

from typing import Any

from ..core.image_view import image_status
from ..core.template_store import background_path

GOLD = "#D6A43A"


def update_fields_overlay(
    app: Any,
    bg_info: dict | None = None,
    refresh_layers: bool = True,
    refresh_status: bool = True,
) -> None:
    """Draw field bounds and optionally refresh status and layer widgets."""
    if not hasattr(app, "template_canvas"):
        return
    canvas = app.template_canvas
    app.template_clear_fields_overlay()
    app.template_clear_smart_guides()
    template = app.template_current()

    if refresh_status and bg_info is None:
        try:
            bg_path = str(background_path(app.template_selected_name, template))
            bg_info = image_status(bg_path)
        except Exception:
            bg_info = {"name": "?", "exists": False}
    elif bg_info is None:
        bg_info = {"name": "?", "exists": False}

    for idx, field in enumerate(template.get("fields", [])):
        if field.get("hidden", False):
            continue
        x1, y1, x2, y2 = app.template_field_screen_rect(field)
        selected = idx == app.template_selected_field or idx in getattr(app, 'template_selected_fields', set())
        outline = GOLD if selected else "#BCA870"
        width = 3 if selected else 2

        canvas.create_rectangle(
            x1, y1, x2, y2,
            fill="#D6A43A",
            stipple="gray25",
            outline=outline,
            width=width,
            tags=("template_overlay",)
        )

        label_text = field.get("name", f"field_{idx+1}")
        if field.get("uppercase", True):
            label_text = label_text.upper()

        canvas.create_text(
            (x1 + x2) // 2,
            (y1 + y2) // 2,
            text=label_text,
            fill=field.get("text_color", "#FFFFFF"),
            font=("Arial", max(10, min(28, int(field.get("font_size", 90) / 5))), "bold"),
            tags=("template_overlay",)
        )

        canvas.create_text(
            x1 + 5, y1 + 5,
            text=field.get("name", f"field_{idx+1}"),
            anchor="nw",
            fill="#111111",
            font=("Arial", 9, "bold"),
            tags=("template_overlay",)
        )

        if selected:
            for _name, hx, hy in app.template_handle_points(x1, y1, x2, y2):
                canvas.create_rectangle(
                    hx - 6, hy - 6, hx + 6, hy + 6,
                    fill=GOLD,
                    outline="#111111",
                    tags=("template_overlay",)
                )

    if refresh_status and hasattr(app, "template_status_label"):
        selected_count = len(getattr(app, "template_selected_fields", set()))
        if selected_count > 1:
            app.template_status_label.configure(
                text=f"{app.template_selected_name} | {selected_count} Felder ausgewählt | BG: {bg_info.get('name', '?')}",
                text_color="#8FE6A0"
            )
        elif app.template_selected_field is not None and 0 <= app.template_selected_field < len(template.get("fields", [])):
            f = template["fields"][app.template_selected_field]
            app.template_status_label.configure(
                text=f"{app.template_selected_name} | {f['name']} | {f['width']}×{f['height']} @ {f['x']}/{f['y']} | BG: {bg_info.get('name', '?')}",
                text_color="#8FE6A0"
            )
        else:
            app.template_status_label.configure(
                text=f"{app.template_selected_name} | Felder: {len(template.get('fields', []))} | BG: {bg_info.get('name', '?')}",
                text_color="#8FE6A0"
            )

    if refresh_layers and hasattr(app, "template_layers_body"):
        app.template_build_layers_panel()
