"""Timed Card Creator -> OBS control integration for VADAFOK Studio 2.21.3."""

from __future__ import annotations

from pathlib import Path
from typing import Any
import json

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
    "Custom...": "custom",
}

_CUSTOM_MIN_SECONDS = 1
_CUSTOM_MAX_SECONDS = 3600

_SETTINGS_DIR = Path.home() / ".vadafok_studio"
_SETTINGS_FILE = _SETTINGS_DIR / "card_creator_obs_settings.json"
_DEFAULT_DURATION = "Until Hidden"
_DEFAULT_CUSTOM_SECONDS = 120


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


def _load_duration_settings() -> dict[str, Any]:
    defaults = {
        "duration": _DEFAULT_DURATION,
        "custom_seconds": _DEFAULT_CUSTOM_SECONDS,
    }

    try:
        if not _SETTINGS_FILE.exists():
            return defaults

        data = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
        duration = str(data.get("duration", _DEFAULT_DURATION)).strip()
        custom_seconds = int(data.get("custom_seconds", _DEFAULT_CUSTOM_SECONDS))

        if duration not in _DURATION_OPTIONS:
            duration = _DEFAULT_DURATION

        if not (_CUSTOM_MIN_SECONDS <= custom_seconds <= _CUSTOM_MAX_SECONDS):
            custom_seconds = _DEFAULT_CUSTOM_SECONDS

        return {
            "duration": duration,
            "custom_seconds": custom_seconds,
        }
    except Exception:
        return defaults


def _save_duration_settings(app: Any) -> None:
    try:
        duration = _selected_duration_label(app)
        custom_seconds = _custom_duration_seconds(app, show_error=False)

        if custom_seconds is None:
            custom_seconds = int(
                getattr(
                    app,
                    "_card_creator_obs_last_custom_seconds",
                    _DEFAULT_CUSTOM_SECONDS,
                )
            )

        if not (_CUSTOM_MIN_SECONDS <= custom_seconds <= _CUSTOM_MAX_SECONDS):
            custom_seconds = _DEFAULT_CUSTOM_SECONDS

        _SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
        _SETTINGS_FILE.write_text(
            json.dumps(
                {
                    "duration": duration,
                    "custom_seconds": custom_seconds,
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )
    except Exception:
        pass


def _selected_duration_label(app: Any) -> str:
    duration_var = getattr(app, "_card_creator_obs_duration_var", None)
    if duration_var is None:
        return "Until Hidden"
    value = str(duration_var.get()).strip()
    return value if value in _DURATION_OPTIONS else "Until Hidden"


def _custom_duration_seconds(app: Any, *, show_error: bool = False) -> int | None:
    custom_var = getattr(app, "_card_creator_obs_custom_duration_var", None)
    raw_value = str(custom_var.get()).strip() if custom_var is not None else ""

    try:
        seconds = int(raw_value)
    except (TypeError, ValueError):
        seconds = None

    if seconds is None or not (_CUSTOM_MIN_SECONDS <= seconds <= _CUSTOM_MAX_SECONDS):
        if show_error:
            messagebox.showwarning(
                "Ungültige Anzeigedauer",
                "Bitte eine gültige Dauer zwischen 1 und 3600 Sekunden eingeben.",
            )
        return None

    # Eingaben wie "00120" oder " 60 " werden sichtbar bereinigt.
    if custom_var is not None:
        try:
            custom_var.set(str(seconds))
        except Exception:
            pass

    app._card_creator_obs_last_custom_seconds = seconds
    return seconds


def _normalize_custom_duration(app: Any, *, show_error: bool = False) -> bool:
    seconds = _custom_duration_seconds(app, show_error=show_error)
    if seconds is None:
        return False

    _save_duration_settings(app)
    return True


def _selected_duration_seconds(app: Any, *, show_error: bool = False) -> int | None:
    label = _selected_duration_label(app)
    value = _DURATION_OPTIONS[label]

    if value == "custom":
        return _custom_duration_seconds(app, show_error=show_error)

    return value


def _duration_display_text(app: Any, seconds: int | None) -> str:
    label = _selected_duration_label(app)

    if seconds is None:
        return "Until Hidden"

    if label == "Custom...":
        return f"Custom: {seconds} Seconds"

    return f"Auto Hide: {seconds} Seconds"


def _set_custom_duration_visibility(app: Any) -> None:
    frame = getattr(app, "_card_creator_obs_custom_duration_frame", None)
    if frame is None:
        return

    try:
        if _selected_duration_label(app) == "Custom...":
            frame.grid()
            entry = getattr(app, "_card_creator_obs_custom_duration_entry", None)
            if entry is not None:
                entry.focus_set()
        else:
            frame.grid_remove()
    except Exception:
        pass


def _on_duration_changed(app: Any, _value: str) -> None:
    _set_custom_duration_visibility(app)
    _save_duration_settings(app)
    _refresh_obs_controls(app, schedule_next=False)


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
                if remaining is not None and _selected_duration_label(app) == "Custom...":
                    duration_text = f"CUSTOM  •  AUTO HIDE IN {remaining}s"
                elif remaining is not None:
                    duration_text = f"AUTO HIDE IN {remaining}s"
                elif _selected_duration_label(app) == "Until Hidden":
                    duration_text = "UNTIL HIDDEN"
                elif _selected_duration_label(app) == "Custom...":
                    custom_seconds = _custom_duration_seconds(app, show_error=False)
                    duration_text = (
                        f"CUSTOM  •  AUTO HIDE IN {remaining}s"
                        if remaining is not None
                        else (
                            f"CUSTOM {custom_seconds}s"
                            if custom_seconds is not None
                            else "CUSTOM"
                        )
                    )
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
        duration_label = _selected_duration_label(self)
        duration_seconds = _selected_duration_seconds(
            self,
            show_error=(duration_label == "Custom..."),
        )

        if duration_label == "Custom..." and duration_seconds is None:
            self.obs.enable_source(scene_name, source_name, False)
            _set_render_status(self, "Ungültige Custom-Dauer. Karte wurde nicht eingeblendet.", _COLOR_OFFLINE)
            _set_obs_status(self, f"OBS STATUS  •  HIDDEN  •  {source_name}", _COLOR_HIDDEN)
            return

        if duration_label == "Custom...":
            _normalize_custom_duration(self, show_error=False)

        _save_duration_settings(self)
        _schedule_auto_hide(self, duration_seconds)
        duration_text = _duration_display_text(self, duration_seconds)
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

        status_label.grid_configure(row=8, column=0, columnspan=2, pady=(8, 0), sticky="w")

        duration_title = ctk.CTkLabel(
            action_frame,
            text="DISPLAY DURATION",
            anchor="w",
            text_color="#D6C27A",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        duration_title.grid(row=2, column=0, columnspan=2, padx=0, pady=(8, 3), sticky="ew")

        saved_settings = _load_duration_settings()
        saved_duration = str(saved_settings.get("duration", _DEFAULT_DURATION))
        saved_custom_seconds = int(
            saved_settings.get("custom_seconds", _DEFAULT_CUSTOM_SECONDS)
        )

        duration_var = ctk.StringVar(value=saved_duration)
        duration_menu = ctk.CTkOptionMenu(
            action_frame,
            variable=duration_var,
            values=list(_DURATION_OPTIONS.keys()),
            height=34,
            fg_color="#292929",
            button_color="#4B4230",
            button_hover_color="#665A40",
            text_color="#F2E2B6",
            command=lambda value: _on_duration_changed(app, value),
        )
        duration_menu.grid(row=3, column=0, columnspan=2, padx=0, pady=(0, 2), sticky="ew")

        app._card_creator_obs_last_custom_seconds = saved_custom_seconds
        custom_duration_var = ctk.StringVar(value=str(saved_custom_seconds))

        custom_duration_frame = ctk.CTkFrame(
            action_frame,
            fg_color="transparent",
        )
        custom_duration_frame.grid(
            row=4,
            column=0,
            columnspan=2,
            padx=0,
            pady=(2, 6),
            sticky="ew",
        )
        custom_duration_frame.grid_columnconfigure(1, weight=1)

        custom_label = ctk.CTkLabel(
            custom_duration_frame,
            text="CUSTOM DURATION",
            anchor="w",
            text_color="#D6C27A",
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        custom_label.grid(row=0, column=0, padx=(0, 8), sticky="w")

        custom_entry = ctk.CTkEntry(
            custom_duration_frame,
            textvariable=custom_duration_var,
            width=90,
            justify="center",
            placeholder_text="120",
        )
        custom_entry.grid(row=0, column=1, sticky="ew")
        custom_entry.bind(
            "<FocusOut>",
            lambda _event: _normalize_custom_duration(app, show_error=False),
        )
        custom_entry.bind(
            "<Return>",
            lambda _event: _normalize_custom_duration(app, show_error=True),
        )

        custom_unit = ctk.CTkLabel(
            custom_duration_frame,
            text="Seconds",
            anchor="w",
            text_color="#B8B8B8",
        )
        custom_unit.grid(row=0, column=2, padx=(8, 0), sticky="w")

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
        show_button.grid(row=5, column=0, columnspan=2, padx=0, pady=(4, 2), sticky="ew")

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
        hide_button.grid(row=6, column=0, columnspan=2, padx=0, pady=(4, 2), sticky="ew")

        obs_status = ctk.CTkLabel(
            action_frame,
            text="OBS STATUS  •  CHECKING ...",
            anchor="w",
            justify="left",
            wraplength=460,
            text_color=_COLOR_NEUTRAL,
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        obs_status.grid(row=7, column=0, columnspan=2, padx=0, pady=(7, 2), sticky="ew")

        app._card_creator_obs_duration_var = duration_var
        app._card_creator_obs_duration_menu = duration_menu
        app._card_creator_obs_custom_duration_var = custom_duration_var
        app._card_creator_obs_custom_duration_frame = custom_duration_frame
        app._card_creator_obs_custom_duration_entry = custom_entry
        app._card_creator_obs_show_button = show_button
        app._card_creator_obs_hide_button = hide_button
        app._card_creator_obs_status_label = obs_status
        app._card_creator_obs_auto_hide_id = None
        app._card_creator_obs_auto_hide_deadline = None
        app._card_creator_obs_button = show_button

        _set_custom_duration_visibility(app)
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
