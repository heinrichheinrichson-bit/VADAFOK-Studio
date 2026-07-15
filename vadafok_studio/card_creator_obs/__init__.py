"""Card Creator -> OBS control integration for VADAFOK Studio 2.20 RC2."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import customtkinter as ctk
from tkinter import messagebox

_INSTALLED = False

_COLOR_LIVE = "#8FE6A0"
_COLOR_HIDDEN = "#D6C27A"
_COLOR_OFFLINE = "#D86A6A"
_COLOR_NEUTRAL = "#B8B8B8"


def _render_final_card(app: Any) -> Path:
    """Render the current Card Creator state using the selected export profile."""
    render_method = getattr(app, "card_render_to_file", None)
    if not callable(render_method):
        raise RuntimeError("Die Card-Creator-Renderfunktion wurde nicht gefunden.")

    result = render_method(final=True)

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


def _configured_source_name(app: Any) -> str:
    source_var = getattr(app, "scene_card_source", None)
    return str(source_var.get()).strip() if source_var is not None else ""


def _selected_profile(app: Any) -> str:
    profile_var = getattr(app, "card_export_profile", None)
    return str(profile_var.get()).strip() if profile_var is not None else "aktuelles Profil"


def _set_render_status(app: Any, text: str, color: str) -> None:
    label = getattr(app, "card_render_status", None)
    if label is not None:
        try:
            label.configure(text=text, text_color=color)
        except Exception:
            pass


def _set_obs_status(app: Any, text: str, color: str) -> None:
    label = getattr(app, "_card_creator_obs_status_label", None)
    if label is not None:
        try:
            label.configure(text=text, text_color=color)
        except Exception:
            pass


def _source_enabled(app: Any, scene_name: str, source_name: str) -> bool | None:
    """Return source visibility, or None if the source cannot be found."""
    try:
        for item in app.obs.get_scene_sources(scene_name):
            if str(item.get("name", "")).strip() == source_name:
                return bool(item.get("enabled", True))
    except Exception:
        return None
    return None


def _refresh_obs_controls(app: Any, *, schedule_next: bool = True) -> None:
    """Refresh button states and the Card Creator OBS status."""
    show_button = getattr(app, "_card_creator_obs_show_button", None)
    hide_button = getattr(app, "_card_creator_obs_hide_button", None)
    status_label = getattr(app, "_card_creator_obs_status_label", None)

    widgets = (show_button, hide_button, status_label)
    if not all(widget is not None for widget in widgets):
        return

    try:
        if not all(widget.winfo_exists() for widget in widgets):
            return
    except Exception:
        return

    connected = bool(getattr(getattr(app, "obs", None), "connected", False))

    if not connected:
        show_button.configure(state="disabled")
        hide_button.configure(state="disabled")
        _set_obs_status(app, "OBS STATUS  •  NOT CONNECTED", _COLOR_OFFLINE)
    else:
        source_name = _configured_source_name(app)
        if not source_name:
            show_button.configure(state="disabled")
            hide_button.configure(state="disabled")
            _set_obs_status(app, "OBS STATUS  •  SOURCE NOT CONFIGURED", _COLOR_OFFLINE)
        else:
            show_button.configure(state="normal")
            hide_button.configure(state="normal")

            try:
                scene_name = app.current_scene()
                enabled = _source_enabled(app, scene_name, source_name)
            except Exception:
                enabled = None

            if enabled is True:
                profile = _selected_profile(app)
                _set_obs_status(
                    app,
                    f"OBS STATUS  •  LIVE  •  {profile}  •  {source_name}",
                    _COLOR_LIVE,
                )
            elif enabled is False:
                _set_obs_status(
                    app,
                    f"OBS STATUS  •  HIDDEN  •  {source_name}",
                    _COLOR_HIDDEN,
                )
            else:
                _set_obs_status(
                    app,
                    f"OBS STATUS  •  READY  •  {source_name}",
                    _COLOR_NEUTRAL,
                )

    if schedule_next:
        try:
            app.after(1000, lambda: _refresh_obs_controls(app, schedule_next=True))
        except Exception:
            pass


def card_show_current_in_obs(self: Any) -> None:
    """Render the current template and display it through the existing OBS image source."""
    if not getattr(getattr(self, "obs", None), "connected", False):
        _set_render_status(self, "OBS nicht verbunden.", _COLOR_OFFLINE)
        _set_obs_status(self, "OBS STATUS  •  NOT CONNECTED", _COLOR_OFFLINE)
        messagebox.showwarning(
            "SHOW IN OBS",
            "Bitte zuerst im OBS Workflow eine Verbindung zu OBS herstellen.",
        )
        _refresh_obs_controls(self, schedule_next=False)
        return

    source_name = _configured_source_name(self)
    if not source_name:
        _set_render_status(self, "OBS-Bildquelle fehlt.", _COLOR_OFFLINE)
        _set_obs_status(self, "OBS STATUS  •  SOURCE NOT CONFIGURED", _COLOR_OFFLINE)
        messagebox.showwarning(
            "SHOW IN OBS",
            "In den Einstellungen ist keine Scene-Card-Bildquelle eingetragen.",
        )
        _refresh_obs_controls(self, schedule_next=False)
        return

    try:
        _set_render_status(self, "Karte wird für OBS gerendert ...", "#BCA870")
        self.update_idletasks()

        image_path = _render_final_card(self)
        scene_name = self.current_scene()

        self.obs.set_image_file(source_name, image_path)
        self.obs.enable_source(scene_name, source_name, True)

        profile = _selected_profile(self)
        _set_render_status(
            self,
            f"OBS LIVE: {image_path.name} ({profile})",
            _COLOR_LIVE,
        )
        _set_obs_status(
            self,
            f"OBS STATUS  •  LIVE  •  {profile}  •  {source_name}",
            _COLOR_LIVE,
        )
    except Exception as exc:
        _set_render_status(self, f"SHOW IN OBS fehlgeschlagen: {exc}", _COLOR_OFFLINE)
        _set_obs_status(self, "OBS STATUS  •  ERROR", _COLOR_OFFLINE)
        messagebox.showerror("SHOW IN OBS fehlgeschlagen", str(exc))
    finally:
        _refresh_obs_controls(self, schedule_next=False)


def card_hide_from_obs(self: Any) -> None:
    """Hide the configured Scene Card source in the current OBS scene."""
    if not getattr(getattr(self, "obs", None), "connected", False):
        _set_obs_status(self, "OBS STATUS  •  NOT CONNECTED", _COLOR_OFFLINE)
        messagebox.showwarning(
            "HIDE FROM OBS",
            "Bitte zuerst im OBS Workflow eine Verbindung zu OBS herstellen.",
        )
        _refresh_obs_controls(self, schedule_next=False)
        return

    source_name = _configured_source_name(self)
    if not source_name:
        _set_obs_status(self, "OBS STATUS  •  SOURCE NOT CONFIGURED", _COLOR_OFFLINE)
        messagebox.showwarning(
            "HIDE FROM OBS",
            "In den Einstellungen ist keine Scene-Card-Bildquelle eingetragen.",
        )
        _refresh_obs_controls(self, schedule_next=False)
        return

    try:
        scene_name = self.current_scene()
        self.obs.enable_source(scene_name, source_name, False)

        _set_render_status(self, f"OBS HIDDEN: {source_name}", _COLOR_HIDDEN)
        _set_obs_status(
            self,
            f"OBS STATUS  •  HIDDEN  •  {source_name}",
            _COLOR_HIDDEN,
        )
    except Exception as exc:
        _set_render_status(self, f"HIDE FROM OBS fehlgeschlagen: {exc}", _COLOR_OFFLINE)
        _set_obs_status(self, "OBS STATUS  •  ERROR", _COLOR_OFFLINE)
        messagebox.showerror("HIDE FROM OBS fehlgeschlagen", str(exc))
    finally:
        _refresh_obs_controls(self, schedule_next=False)


def _inject_obs_controls(app: Any) -> None:
    """Add SHOW, HIDE and OBS status controls to the existing Card Creator action frame."""
    status_label = getattr(app, "card_render_status", None)
    if status_label is None:
        return

    try:
        action_frame = status_label.master
        if action_frame is None:
            return

        existing = getattr(app, "_card_creator_obs_show_button", None)
        if existing is not None and existing.winfo_exists():
            _refresh_obs_controls(app, schedule_next=False)
            return

        # Existing Card Creator controls occupy rows 0 and 1.
        # RC2 uses rows 2–4 and moves the original render status to row 5.
        status_label.grid_configure(
            row=5,
            column=0,
            columnspan=2,
            pady=(8, 0),
            sticky="w",
        )

        show_button = ctk.CTkButton(
            action_frame,
            text="SHOW IN OBS",
            height=42,
            fg_color="#2F6B3B",
            hover_color="#3F8250",
            text_color="#F2E2B6",
            font=ctk.CTkFont(weight="bold"),
            command=app.card_show_current_in_obs,
        )
        show_button.grid(
            row=2,
            column=0,
            columnspan=2,
            padx=0,
            pady=(8, 2),
            sticky="ew",
        )

        hide_button = ctk.CTkButton(
            action_frame,
            text="HIDE FROM OBS",
            height=38,
            fg_color="#5A3434",
            hover_color="#714242",
            text_color="#F2E2B6",
            font=ctk.CTkFont(weight="bold"),
            command=app.card_hide_from_obs,
        )
        hide_button.grid(
            row=3,
            column=0,
            columnspan=2,
            padx=0,
            pady=(4, 2),
            sticky="ew",
        )

        obs_status = ctk.CTkLabel(
            action_frame,
            text="OBS STATUS  •  CHECKING ...",
            anchor="w",
            justify="left",
            text_color=_COLOR_NEUTRAL,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        obs_status.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=0,
            pady=(7, 2),
            sticky="ew",
        )

        app._card_creator_obs_show_button = show_button
        app._card_creator_obs_hide_button = hide_button
        app._card_creator_obs_status_label = obs_status

        # Keep the RC1 attribute for compatibility with any external checks.
        app._card_creator_obs_button = show_button

        _refresh_obs_controls(app, schedule_next=True)
    except Exception as exc:
        print(f"[Card Creator OBS] Controls konnten nicht eingesetzt werden: {exc}")


def install_card_creator_obs_display() -> None:
    """Install the Card Creator OBS extension once."""
    global _INSTALLED
    if _INSTALLED:
        return

    from vadafok_studio.app import VadafokStudio

    VadafokStudio.card_show_current_in_obs = card_show_current_in_obs
    VadafokStudio.card_hide_from_obs = card_hide_from_obs
    VadafokStudio.card_refresh_obs_controls = _refresh_obs_controls

    original = getattr(VadafokStudio, "show_card_creator_page", None)
    if original is None:
        raise RuntimeError("Card Creator wurde in VadafokStudio nicht gefunden.")

    if not getattr(original, "_vadafok_card_obs_rc2_wrapped", False):
        def wrapped_show_card_creator_page(self: Any, *args: Any, **kwargs: Any):
            result = original(self, *args, **kwargs)
            try:
                _inject_obs_controls(self)
            except Exception as exc:
                print(f"[Card Creator OBS] Integration fehlgeschlagen: {exc}")
            return result

        wrapped_show_card_creator_page._vadafok_card_obs_rc2_wrapped = True
        wrapped_show_card_creator_page.__name__ = getattr(
            original, "__name__", "show_card_creator_page"
        )
        wrapped_show_card_creator_page.__doc__ = getattr(original, "__doc__", None)
        VadafokStudio.show_card_creator_page = wrapped_show_card_creator_page

    _INSTALLED = True


__all__ = ["install_card_creator_obs_display"]
