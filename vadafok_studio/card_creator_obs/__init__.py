"""Timed Card Creator -> OBS control integration for VADAFOK Studio 2.21 RC1."""

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

_DURATION_OPTIONS = {
    "Until Hidden": None,
    "30 Seconds": 30,
    "60 Seconds": 60,
}


def _render_final_card(app: Any) -> Path:
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


def _selected_duration_label(app: Any) -> str:
    duration_var = getattr(app, "_card_creator_obs_duration_var", None)
    if duration_var is None:
        return "Until Hidden"
    value = str(duration_var.get()).strip()
    return value if value in _DURATION_OPTIONS else "Until Hidden"


def _selected_duration_seconds(app: Any) -> int | None:
    return _DURATION_OPTIONS[_selected_duration_label(app)]


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
    try:
        for item in app.obs.get_scene_sources(scene_name):
            if str(item.get("name", "")).strip() == source_name:
                return bool(item.get("enabled", True))
    except Exception:
        return None
    return None


def _cancel_auto_hide(app: Any) -> None:
    timer_id = getattr(app, "_card_creator_obs_auto_hide_id", None)
    if timer_id is not None:
        try:
            app.after_cancel(timer_id)
        except Exception:
            pass
    app._card_creator_obs_auto_hide_id = None
    app._card_creator_obs_auto_hide_deadline = None


def _schedule_auto_hide(app: Any, seconds: int | None) -> None:
    _cancel_auto_hide(app)
    if seconds is None:
        return
    try:
        now_ms = int(app.tk.call("clock", "milliseconds"))
        app._card_creator_obs_auto_hide_deadline = now_ms + (seconds * 1000)
    except Exception:
        app._card_creator_obs_auto_hide_deadline = None
    app._card_creator_obs_auto_hide_id = app.after(
        seconds * 1000,
        lambda: _auto_hide_now(app),
    )


def _auto_hide_now(app: Any) -> None:
    app._card_creator_obs_auto_hide_id = None
    app._card_creator_obs_auto_hide_deadline = None
    if not getattr(getattr(app, "obs", None), "connected", False):
        _set_obs_status(app, "OBS STATUS  •  NOT CONNECTED", _COLOR_OFFLINE)
        return
    source_name = _configured_source_name(app)
    if not source_name:
        _set_obs_status(app, "OBS STATUS  •  SOURCE NOT CONFIGURED", _COLOR_OFFLINE)
        return
    try:
        scene_name = app.current_scene()
        app.obs.enable_source(scene_name, source_name, False)
        _set_render_status(app, f"OBS AUTO-HIDDEN: {source_name}", _COLOR_HIDDEN)
        _set_obs_status(app, f"OBS STATUS  •  HIDDEN  •  {source_name}", _COLOR_HIDDEN)
    except Exception as exc:
        _set_render_status(app, f"AUTO-HIDE fehlgeschlagen: {exc}", _COLOR_OFFLINE)
        _set_obs_status(app, "OBS STATUS  •  AUTO-HIDE ERROR", _COLOR_OFFLINE)


def _remaining_seconds(app: Any) -> int | None:
    deadline = getattr(app, "_card_creator_obs_auto_hide_deadline", None)
    if deadline is None:
        return None
    try:
        now = int(app.tk.call("clock", "milliseconds"))
        return (max(0, int(deadline) - now) + 999) // 1000
    except Exception:
        return None


def _refresh_obs_controls(app: Any, *, schedule_next: bool = True) -> None:
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
        _cancel_auto_hide(app)
        show_button.configure(state="disabled")
        hide_button.configure(state="disabled")
        _set_obs_status(app, "OBS STATUS  •  NOT CONNECTED", _COLOR_OFFLINE)
    else:
        source_name = _configured_source_name(app)
        if not source_name:
            _cancel_auto_hide(app)
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
                remaining = _remaining_seconds(app)
                if remaining is not None:
                    duration_text = f"AUTO HIDE IN {remaining}s"
                elif _selected_duration_label(app) == "Until Hidden":
                    duration_text = "UNTIL HIDDEN"
                else:
                    duration_text = _selected_duration_label(app).upper()
                _set_obs_status(
                    app,
                    f"OBS STATUS  •  LIVE  •  {duration_text}  •  {profile}  •  {source_name}",
                    _COLOR_LIVE,
                )
            elif enabled is False:
                _cancel_auto_hide(app)
                _set_obs_status(app, f"OBS STATUS  •  HIDDEN  •  {source_name}", _COLOR_HIDDEN)
            else:
                _set_obs_status(app, f"OBS STATUS  •  READY  •  {source_name}", _COLOR_NEUTRAL)

    if schedule_next:
        try:
            app.after(1000, lambda: _refresh_obs_controls(app, schedule_next=True))
        except Exception:
            pass


def card_show_current_in_obs(self: Any) -> None:
    if not getattr(getattr(self, "obs", None), "connected", False):
        _set_render_status(self, "OBS nicht verbunden.", _COLOR_OFFLINE)
        _set_obs_status(self, "OBS STATUS  •  NOT CONNECTED", _COLOR_OFFLINE)
        messagebox.showwarning("SHOW IN OBS", "Bitte zuerst im OBS Workflow eine Verbindung zu OBS herstellen.")
        _refresh_obs_controls(self, schedule_next=False)
        return

    source_name = _configured_source_name(self)
    if not source_name:
        _set_render_status(self, "OBS-Bildquelle fehlt.", _COLOR_OFFLINE)
        _set_obs_status(self, "OBS STATUS  •  SOURCE NOT CONFIGURED", _COLOR_OFFLINE)
        messagebox.showwarning("SHOW IN OBS", "In den Einstellungen ist keine Scene-Card-Bildquelle eingetragen.")
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
        duration_seconds = _selected_duration_seconds(self)
        _schedule_auto_hide(self, duration_seconds)

        duration_text = "Until Hidden" if duration_seconds is None else f"Auto Hide: {duration_seconds} Seconds"
        _set_render_status(self, f"OBS LIVE: {image_path.name} ({profile}, {duration_text})", _COLOR_LIVE)
        _set_obs_status(
            self,
            f"OBS STATUS  •  LIVE  •  {duration_text.upper()}  •  {profile}  •  {source_name}",
            _COLOR_LIVE,
        )
    except Exception as exc:
        _cancel_auto_hide(self)
        _set_render_status(self, f"SHOW IN OBS fehlgeschlagen: {exc}", _COLOR_OFFLINE)
        _set_obs_status(self, "OBS STATUS  •  ERROR", _COLOR_OFFLINE)
        messagebox.showerror("SHOW IN OBS fehlgeschlagen", str(exc))
    finally:
        _refresh_obs_controls(self, schedule_next=False)


def card_hide_from_obs(self: Any) -> None:
    _cancel_auto_hide(self)
    if not getattr(getattr(self, "obs", None), "connected", False):
        _set_obs_status(self, "OBS STATUS  •  NOT CONNECTED", _COLOR_OFFLINE)
        messagebox.showwarning("HIDE FROM OBS", "Bitte zuerst im OBS Workflow eine Verbindung zu OBS herstellen.")
        _refresh_obs_controls(self, schedule_next=False)
        return

    source_name = _configured_source_name(self)
    if not source_name:
        _set_obs_status(self, "OBS STATUS  •  SOURCE NOT CONFIGURED", _COLOR_OFFLINE)
        messagebox.showwarning("HIDE FROM OBS", "In den Einstellungen ist keine Scene-Card-Bildquelle eingetragen.")
        _refresh_obs_controls(self, schedule_next=False)
        return

    try:
        scene_name = self.current_scene()
        self.obs.enable_source(scene_name, source_name, False)
        _set_render_status(self, f"OBS HIDDEN: {source_name}", _COLOR_HIDDEN)
        _set_obs_status(self, f"OBS STATUS  •  HIDDEN  •  {source_name}", _COLOR_HIDDEN)
    except Exception as exc:
        _set_render_status(self, f"HIDE FROM OBS fehlgeschlagen: {exc}", _COLOR_OFFLINE)
        _set_obs_status(self, "OBS STATUS  •  ERROR", _COLOR_OFFLINE)
        messagebox.showerror("HIDE FROM OBS fehlgeschlagen", str(exc))
    finally:
        _refresh_obs_controls(self, schedule_next=False)


def _inject_obs_controls(app: Any) -> None:
    status_label = getattr(app, "card_render_status", None)
    if status_label is None:
        return
    try:
        action_frame = status_label.master
        existing = getattr(app, "_card_creator_obs_show_button", None)
        if existing is not None and existing.winfo_exists():
            _refresh_obs_controls(app, schedule_next=False)
            return

        status_label.grid_configure(row=7, column=0, columnspan=2, pady=(8, 0), sticky="w")

        duration_title = ctk.CTkLabel(
            action_frame,
            text="DISPLAY DURATION",
            anchor="w",
            text_color="#D6C27A",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        duration_title.grid(row=2, column=0, columnspan=2, padx=0, pady=(8, 3), sticky="ew")

        duration_var = ctk.StringVar(value="Until Hidden")
        duration_menu = ctk.CTkOptionMenu(
            action_frame,
            variable=duration_var,
            values=list(_DURATION_OPTIONS.keys()),
            height=34,
            fg_color="#292929",
            button_color="#4B4230",
            button_hover_color="#665A40",
            text_color="#F2E2B6",
            command=lambda _value: _refresh_obs_controls(app, schedule_next=False),
        )
        duration_menu.grid(row=3, column=0, columnspan=2, padx=0, pady=(0, 6), sticky="ew")

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
        show_button.grid(row=4, column=0, columnspan=2, padx=0, pady=(4, 2), sticky="ew")

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
        hide_button.grid(row=5, column=0, columnspan=2, padx=0, pady=(4, 2), sticky="ew")

        obs_status = ctk.CTkLabel(
            action_frame,
            text="OBS STATUS  •  CHECKING ...",
            anchor="w",
            justify="left",
            wraplength=460,
            text_color=_COLOR_NEUTRAL,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        obs_status.grid(row=6, column=0, columnspan=2, padx=0, pady=(7, 2), sticky="ew")

        app._card_creator_obs_duration_var = duration_var
        app._card_creator_obs_duration_menu = duration_menu
        app._card_creator_obs_show_button = show_button
        app._card_creator_obs_hide_button = hide_button
        app._card_creator_obs_status_label = obs_status
        app._card_creator_obs_auto_hide_id = None
        app._card_creator_obs_auto_hide_deadline = None
        app._card_creator_obs_button = show_button

        _refresh_obs_controls(app, schedule_next=True)
    except Exception as exc:
        print(f"[Timed Card Creator OBS] Controls konnten nicht eingesetzt werden: {exc}")


def install_card_creator_obs_display() -> None:
    global _INSTALLED
    if _INSTALLED:
        return

    from vadafok_studio.app import VadafokStudio

    VadafokStudio.card_show_current_in_obs = card_show_current_in_obs
    VadafokStudio.card_hide_from_obs = card_hide_from_obs
    VadafokStudio.card_refresh_obs_controls = _refresh_obs_controls
    VadafokStudio.card_cancel_auto_hide = _cancel_auto_hide

    original = getattr(VadafokStudio, "show_card_creator_page", None)
    if original is None:
        raise RuntimeError("Card Creator wurde in VadafokStudio nicht gefunden.")

    if not getattr(original, "_vadafok_card_obs_221_wrapped", False):
        def wrapped_show_card_creator_page(self: Any, *args: Any, **kwargs: Any):
            result = original(self, *args, **kwargs)
            try:
                _inject_obs_controls(self)
            except Exception as exc:
                print(f"[Timed Card Creator OBS] Integration fehlgeschlagen: {exc}")
            return result

        wrapped_show_card_creator_page._vadafok_card_obs_221_wrapped = True
        wrapped_show_card_creator_page.__name__ = getattr(original, "__name__", "show_card_creator_page")
        wrapped_show_card_creator_page.__doc__ = getattr(original, "__doc__", None)
        VadafokStudio.show_card_creator_page = wrapped_show_card_creator_page

    _INSTALLED = True


__all__ = ["install_card_creator_obs_display"]
