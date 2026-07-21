"""Actions that send or apply the selected Library asset."""

from __future__ import annotations

from typing import Any
from tkinter import messagebox

from ..core.config import save_config


def use_as_caption_banner(app: Any) -> None:
    """Persist the selected banner and update OBS when available."""
    item = getattr(app, "selected_item", None)
    if item is None:
        messagebox.showwarning("Banner", "Bitte zuerst ein Banner auswählen.")
        return
    if item.kind != "image":
        messagebox.showwarning(
            "Banner", "Nur Bilder können als Caption-Banner verwendet werden.",
        )
        return

    picker_mode = bool(getattr(app, "library_banner_picker_mode", False))
    app.config_data["selected_banner_path"] = str(item.path)
    target_slot = getattr(app, "library_banner_target_slot", None)
    if picker_mode and isinstance(target_slot, int) and 0 <= target_slot < 4:
        slots = app.config_data.get("live_card_banner_slots", [])
        slots = list(slots) if isinstance(slots, list) else []
        slots = (slots + ["", "", "", ""])[:4]
        slots[target_slot] = str(item.path)
        app.config_data["live_card_banner_slots"] = slots
        app.config_data["live_card_banner_slots_initialized"] = True
    save_config(app.config_data)

    obs_warning = None
    if app.ensure_obs_ready():
        try:
            app.obs.set_image_file(
                app.caption_banner_source.get().strip(), item.path,
            )
        except Exception:
            obs_warning = (
                "Das Banner wurde im Studio gespeichert, aber die "
                f"OBS-Bildquelle '{app.caption_banner_source.get().strip()}' "
                "wurde nicht gefunden."
            )

    if picker_mode:
        app.library_banner_picker_mode = False
        app.library_banner_target_slot = None
        app.library_return_page = None
        app.show_live_card()
        _refresh_render_preview(app)
        if obs_warning:
            app.after(
                150,
                lambda text=obs_warning: messagebox.showwarning(
                    "Caption Banner Source nicht gefunden", text,
                ),
            )
        return

    if hasattr(app, "message_box"):
        _refresh_render_preview(app)
    if obs_warning:
        messagebox.showwarning(
            "Caption Banner Source nicht gefunden", obs_warning,
        )
    else:
        messagebox.showinfo(
            "Banner", f"Caption-Banner gewechselt:\n{item.name}",
        )


def _refresh_render_preview(app: Any) -> None:
    try:
        app.update_render_preview()
    except Exception:
        pass


def show_as_scene_card(app: Any) -> None:
    item = getattr(app, "selected_item", None)
    if item is None:
        return
    if item.kind != "image":
        messagebox.showwarning(
            "Scene Card", "Nur Bilder können als Scene Card angezeigt werden.",
        )
        return
    if not app.obs.connected:
        messagebox.showwarning(
            "Nicht verbunden", "Bitte zuerst OBS verbinden.",
        )
        return
    try:
        scene = app.current_scene()
        source = app.scene_card_source.get().strip()
        app.obs.set_image_file(source, item.path)
        app.obs.enable_source(scene, source, True)
    except Exception as error:
        messagebox.showerror("Scene Card fehlgeschlagen", str(error))


def open_live_card(app: Any) -> None:
    item = getattr(app, "selected_item", None)
    if item is None:
        return
    app.show_live_card()
    app.set_message(
        item.path.stem.replace("_", " ").replace("-", " ").upper()
    )
