"""Canvas background rendering for the Template Editor."""

from __future__ import annotations

from typing import Any
import tkinter as tk

from ..core.image_view import fit_image_to_box, image_status, pil_to_tk_photo_data
from ..core.template_store import background_path


def draw_canvas(app: Any, refresh_layers: bool = True) -> None:
    """Draw the background and delegate field-overlay rendering."""
    if not hasattr(app, "template_canvas"):
        return

    # Use in-memory working data while editing, otherwise click/drag would reset the fields.
    template = app.template_current()

    canvas = app.template_canvas
    canvas.update_idletasks()

    cw = max(600, canvas.winfo_width())
    ch = max(360, canvas.winfo_height())

    bg_path = str(background_path(app.template_selected_name, template))
    bg_info = image_status(bg_path)

    app.template_bg_photo = None
    app.template_canvas_design_size = (1280, 720)

    if bg_path and bg_info["exists"]:
        try:
            original = app.template_load_background_image(bg_path)
            app.template_canvas_design_size = original.size
            _display, base_scale, _offset = fit_image_to_box(original, cw, ch, padding=40)
            scale = base_scale * float(getattr(app, "template_zoom_factor", 1.0))
            display = original.resize((max(1, int(original.size[0] * scale)), max(1, int(original.size[1] * scale))))
            base_offset = ((cw - display.size[0]) // 2, (ch - display.size[1]) // 2)
            offset = (
                base_offset[0] + int(getattr(app, "template_pan_x", 0)),
                base_offset[1] + int(getattr(app, "template_pan_y", 0))
            )
            app.template_canvas_scale = scale
            app.template_canvas_offset = offset
            # Keep the old canvas visible while loading and scaling. Clear it
            # only after the replacement image is fully prepared.
            next_bg_photo = tk.PhotoImage(data=pil_to_tk_photo_data(display))
            canvas.delete("all")
            app.template_bg_photo = next_bg_photo
            canvas.create_image(offset[0], offset[1], image=app.template_bg_photo, anchor="nw", tags="background")
            canvas.create_rectangle(offset[0], offset[1], offset[0] + display.size[0], offset[1] + display.size[1], outline="#3A2A0D", width=2)
        except Exception as e:
            app.template_canvas_scale = min((cw - 40) / 1280, (ch - 40) / 720) * float(getattr(app, 'template_zoom_factor', 1.0))
            app.template_canvas_offset = (((cw - int(1280 * app.template_canvas_scale)) // 2) + int(getattr(app, 'template_pan_x', 0)), ((ch - int(720 * app.template_canvas_scale)) // 2) + int(getattr(app, 'template_pan_y', 0)))
            ox, oy = app.template_canvas_offset
            dw, dh = int(1280 * app.template_canvas_scale), int(720 * app.template_canvas_scale)
            canvas.delete("all")
            canvas.create_rectangle(ox, oy, ox + dw, oy + dh, fill="#111111", outline="#3A2A0D", width=2)
            canvas.create_text(ox + 20, oy + 20, text=f"Background Fehler:\n{e}", anchor="nw", fill="#D86A6A", font=("Arial", 14, "bold"))
    else:
        app.template_canvas_scale = min((cw - 40) / 1280, (ch - 40) / 720) * float(getattr(app, 'template_zoom_factor', 1.0))
        app.template_canvas_offset = (((cw - int(1280 * app.template_canvas_scale)) // 2) + int(getattr(app, 'template_pan_x', 0)), ((ch - int(720 * app.template_canvas_scale)) // 2) + int(getattr(app, 'template_pan_y', 0)))
        ox, oy = app.template_canvas_offset
        dw, dh = int(1280 * app.template_canvas_scale), int(720 * app.template_canvas_scale)
        canvas.delete("all")
        canvas.create_rectangle(ox, oy, ox + dw, oy + dh, fill="#111111", outline="#3A2A0D", width=2)

    ox, oy = app.template_canvas_offset
    status_text = (
        f"Background: {bg_info['name']}\n"
        f"Status: {'✔ Datei gefunden' if bg_info['exists'] else '✖ kein/fehlender Hintergrund'}\n"
        f"Größe: {bg_info['size'] or '-'}"
    )
    canvas.create_text(ox + 18, oy + 18, text=status_text, anchor="nw", fill="#D6A43A", font=("Arial", 12, "bold"))

    app.template_update_fields_overlay(bg_info, refresh_layers=refresh_layers)
