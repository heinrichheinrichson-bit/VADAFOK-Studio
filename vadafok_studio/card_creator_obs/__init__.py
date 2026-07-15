"""Card Creator -> OBS live display integration for VADAFOK Studio 2.20 RC1."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import customtkinter as ctk
from tkinter import messagebox

_INSTALLED = False


def _render_final_card(app: Any) -> Path:
    """Render the current Card Creator state using the selected export profile."""
    render_method = getattr(app, "card_render_to_file", None)
    if not callable(render_method):
        raise RuntimeError("Die Card-Creator-Renderfunktion wurde nicht gefunden.")

    result = render_method(final=True)

    # Be tolerant if a future render method returns additional metadata.
    if isinstance(result, (tuple, list)):
        result = result[0] if result else None

    if result is None:
        result = getattr(app, "card_creator_last_render", None)

    if not result:
        raise RuntimeError("Die aktuelle Karte konnte nicht gerendert werden.")

    path = Path(result).expanduser().resolve()
    if not path.exists() or not path.is_file():
        raise RuntimeError(f"Die gerenderte Bilddatei wurde nicht gefunden:\n{path}")

    app.card_creator_last_render = path
    return path


def _set_status(app: Any, text: str, color: str) -> None:
    label = getattr(app, "card_render_status", None)
    if label is not None:
        try:
            label.configure(text=text, text_color=color)
        except Exception:
            pass


def card_show_current_in_obs(self: Any) -> None:
    """Render the current template and display it through the existing OBS image source."""
    if not getattr(getattr(self, "obs", None), "connected", False):
        _set_status(self, "OBS nicht verbunden.", "#D86A6A")
        messagebox.showwarning(
            "SHOW IN OBS",
            "Bitte zuerst im OBS Workflow eine Verbindung zu OBS herstellen.",
        )
        return

    source_var = getattr(self, "scene_card_source", None)
    source_name = str(source_var.get()).strip() if source_var is not None else ""
    if not source_name:
        _set_status(self, "OBS-Bildquelle fehlt.", "#D86A6A")
        messagebox.showwarning(
            "SHOW IN OBS",
            "In den Einstellungen ist keine Scene-Card-Bildquelle eingetragen.",
        )
        return

    try:
        _set_status(self, "Karte wird für OBS gerendert ...", "#BCA870")
        self.update_idletasks()

        image_path = _render_final_card(self)
        scene_name = self.current_scene()

        # Reuse the existing OBSController API and existing Scene Card image source.
        self.obs.set_image_file(source_name, image_path)
        self.obs.enable_source(scene_name, source_name, True)

        profile = (
            str(self.card_export_profile.get())
            if getattr(self, "card_export_profile", None) is not None
            else "aktuelles Profil"
        )
        _set_status(
            self,
            f"OBS LIVE: {image_path.name} ({profile})",
            "#8FE6A0",
        )
        messagebox.showinfo(
            "SHOW IN OBS",
            "Die aktuell erstellte Karte wird jetzt in OBS angezeigt.\n\n"
            f"Szene: {scene_name}\n"
            f"Quelle: {source_name}\n"
            f"Profil: {profile}\n"
            f"Datei: {image_path.name}",
        )
    except Exception as exc:
        _set_status(self, f"SHOW IN OBS fehlgeschlagen: {exc}", "#D86A6A")
        messagebox.showerror("SHOW IN OBS fehlgeschlagen", str(exc))


def _inject_show_button(app: Any) -> None:
    """Add the SHOW IN OBS button to the existing Card Creator action frame."""
    status_label = getattr(app, "card_render_status", None)
    if status_label is None:
        return

    try:
        action_frame = status_label.master
        if action_frame is None:
            return

        existing = getattr(app, "_card_creator_obs_button", None)
        if existing is not None and existing.winfo_exists():
            return

        # The original status label is at row 2. Move it down and use row 2 for
        # the new action, without replacing any existing Card Creator controls.
        status_label.grid_configure(row=3, column=0, columnspan=2, pady=(8, 0), sticky="w")

        button = ctk.CTkButton(
            action_frame,
            text="SHOW IN OBS",
            height=42,
            fg_color="#2F6B3B",
            hover_color="#3F8250",
            text_color="#F2E2B6",
            font=ctk.CTkFont(weight="bold"),
            command=app.card_show_current_in_obs,
        )
        button.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=0,
            pady=(8, 2),
            sticky="ew",
        )
        app._card_creator_obs_button = button
    except Exception as exc:
        print(f"[Card Creator OBS] Button konnte nicht eingesetzt werden: {exc}")


def install_card_creator_obs_display() -> None:
    """Install the Card Creator OBS extension once."""
    global _INSTALLED
    if _INSTALLED:
        return

    from vadafok_studio.app import VadafokStudio

    if not hasattr(VadafokStudio, "card_show_current_in_obs"):
        VadafokStudio.card_show_current_in_obs = card_show_current_in_obs

    original = getattr(VadafokStudio, "show_card_creator_page", None)
    if original is None:
        raise RuntimeError("Card Creator wurde in VadafokStudio nicht gefunden.")

    if not getattr(original, "_vadafok_card_obs_wrapped", False):
        def wrapped_show_card_creator_page(self: Any, *args: Any, **kwargs: Any):
            result = original(self, *args, **kwargs)
            try:
                _inject_show_button(self)
            except Exception as exc:
                print(f"[Card Creator OBS] Integration fehlgeschlagen: {exc}")
            return result

        wrapped_show_card_creator_page._vadafok_card_obs_wrapped = True
        wrapped_show_card_creator_page.__name__ = getattr(
            original, "__name__", "show_card_creator_page"
        )
        wrapped_show_card_creator_page.__doc__ = getattr(original, "__doc__", None)
        VadafokStudio.show_card_creator_page = wrapped_show_card_creator_page

    _INSTALLED = True


__all__ = ["install_card_creator_obs_display"]
