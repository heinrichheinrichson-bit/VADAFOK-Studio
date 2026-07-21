"""Template background file actions."""

from __future__ import annotations

from pathlib import Path
from typing import Any
from tkinter import filedialog, messagebox

from ..core.template_store import background_path, save_template


def background_status(app: Any) -> str:
    template = app.template_current()
    configured = template.get("background", "")
    if not configured:
        return "kein Hintergrund"
    resolved = background_path(app.template_selected_name, template)
    return f"{Path(configured).name} ({'OK' if resolved.exists() else 'FEHLT'})"


def choose_background_file(app: Any) -> None:
    path = filedialog.askopenfilename(
        title="Template Hintergrund auswählen",
        filetypes=[
            ("Bilddateien", "*.png *.jpg *.jpeg *.webp"),
            ("PNG-Dateien", "*.png"),
            ("Alle Dateien", "*.*"),
        ],
    )
    if not path:
        return
    app.template_set_background_path(path)
    messagebox.showinfo(
        "Template Background", f"Hintergrund gesetzt:\n{Path(path).name}",
    )


def clear_background(app: Any) -> None:
    template = app.template_current()
    template["background"] = "background.png"
    save_template(app.template_selected_name, template)
    app.template_draw_canvas()
    messagebox.showinfo("Template Background", "Hintergrund entfernt.")
