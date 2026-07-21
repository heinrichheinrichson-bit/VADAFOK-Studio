"""Runtime status and support helpers for the Silent Director."""

from __future__ import annotations

import datetime
import threading
from typing import Any

from ..core import silent_director

GOLD = "#D6A43A"

def director_set_active_action(app: Any, index=None, flush=True):
    """Highlight the currently running timeline action without rebuilding the page."""
    app.director_active_action_index = index

    widgets_map = getattr(app, "director_action_card_widgets", {}) or {}
    for action_index, widgets in widgets_map.items():
        style = widgets.get("style", {})
        active = index is not None and action_index == index

        card = widgets.get("card")
        title = widgets.get("title")
        badge = widgets.get("badge")
        runtime = widgets.get("runtime")

        try:
            if card is not None:
                card.configure(
                    fg_color="#3A321A" if active else style.get("card", "#1B1B1B"),
                    border_color="#F5D76E" if active else style.get("accent", GOLD),
                    border_width=3 if active else 1,
                )
        except Exception:
            pass

        try:
            if title is not None:
                title.configure(
                    text_color="#FFF2A8" if active else style.get("accent", GOLD)
                )
        except Exception:
            pass

        try:
            if badge is not None:
                badge.configure(
                    text="RUN" if active else style.get("badge", "AC"),
                    fg_color="#F5D76E" if active else style.get("accent", GOLD),
                    text_color="#111111",
                )
        except Exception:
            pass

        try:
            if runtime is not None:
                runtime.configure(
                    text="▶ RUNNING NOW" if active else widgets.get("step_text", ""),
                    text_color="#FFF2A8" if active else "#7E7E7E",
                )
        except Exception:
            pass

    if flush:
        try:
            app.update_idletasks()
        except Exception:
            pass


def director_log_add(app: Any, message):
    try:
        stamp = datetime.datetime.now().strftime("%H:%M:%S")
    except Exception:
        stamp = ""
    entry = f"{stamp}  {message}" if stamp else str(message)
    if not hasattr(app, "director_log_entries"):
        app.director_log_entries = []
    app.director_log_entries.append(entry)
    app.director_log_entries = app.director_log_entries[-200:]
    try:
        if hasattr(app, "director_log_text_var"):
            app.director_log_text_var.set("\n".join(app.director_log_entries[-10:]) or "No Director run yet.")
    except Exception:
        pass
    try:
        app.obs_workflow_log(f"Director: {message}")
    except Exception:
        pass


def director_set_status(app: Any, status, current="-", progress=""):
    try:
        app.director_status_var.set(status)
    except Exception:
        pass
    try:
        app.director_current_action_var.set(current or "-")
    except Exception:
        pass
    if progress:
        try:
            app.director_progress_var.set(progress)
        except Exception:
            pass
        try:
            done, total = [float(x.strip()) for x in str(progress).split("/")]
            app.director_progress_percent_var.set(0.0 if total <= 0 else max(0.0, min(1.0, done / total)))
        except Exception:
            pass
    try:
        app.update_idletasks()
    except Exception:
        pass
    active = str(status).upper() in ("RUNNING", "WAITING", "STOPPING")
    color = (
        "#8FE6A0" if status in ("READY", "FINISHED")
        else "#F0C06A" if active
        else "#F08A8A" if status == "ERROR"
        else "#888888"
    )
    try:
        app.director_status_label.configure(text_color=color)
    except Exception:
        pass
    try:
        app.director_run_button.configure(state="disabled" if active else "normal")
        app.director_stop_button.configure(state="normal" if active else "disabled")
    except Exception:
        pass


def director_request_stop(app: Any):
    try:
        status = str(app.director_status_var.get() or "").upper()
    except Exception:
        status = ""
    if status not in ("RUNNING", "WAITING"):
        return False
    app.director_stop_requested = True
    app.director_set_status("STOPPING", "Stop requested", app.director_progress_var.get())
    app.director_log_add("STOP requested")
    return True


def director_action_label(app: Any, action):
    action_type = action.get("type", "")
    if action_type == "switch_scene":
        return f"Switch Scene -> {action.get('scene', '')}"
    if action_type == "show_banner":
        return f"Show Banner -> {action.get('text', '')}"
    if action_type == "show_source":
        return f"Show Source -> {action.get('source', '')}"
    if action_type == "hide_source":
        return f"Hide Source -> {action.get('source', '')}"
    if action_type == "wait":
        return f"WAIT -> {action.get('seconds', '5')} s"
    return str(action_type or "Action")


def silent_director_show_banner_direct(app: Any, text):
    """Show a banner from Silent Director without switching to the Live Card page."""
    if not app.ensure_obs_ready():
        return False

    text = str(text or "").strip()
    if not text:
        return False

    try:
        scene = app.current_scene()
        selected_banner_path = app.config_data.get("selected_banner_path", "")

        if app.caption_engine.get() == "smart_png":
            png = app.render_smart_caption(text)
            app.obs.set_image_file(app.caption_render_source.get().strip(), png)

            try:
                app.obs.enable_source(scene, app.caption_text.get().strip(), False)
            except Exception:
                pass
            try:
                app.obs.enable_source(scene, app.caption_render_source.get().strip(), True)
            except Exception:
                pass
        else:
            if selected_banner_path:
                app.obs.set_image_file(app.caption_banner_source.get().strip(), selected_banner_path)

            app.obs.set_text(app.caption_text.get().strip(), text)

            try:
                app.obs.enable_source(scene, app.caption_render_source.get().strip(), False)
            except Exception:
                pass
            try:
                app.obs.enable_source(scene, app.caption_text.get().strip(), True)
            except Exception:
                pass

        try:
            app.obs.enable_source(scene, app.caption_group.get().strip(), True)
        except Exception:
            pass

        if app.hide_timer:
            app.hide_timer.cancel()
        seconds = max(1, int(app.duration.get()))
        app.hide_timer = threading.Timer(seconds, lambda: app.after(0, app.hide_card))
        app.hide_timer.daemon = True
        app.hide_timer.start()

        try:
            app.obs_workflow_banner_action("SHOW Director Banner", text)
        except Exception:
            pass

        return True

    except Exception as e:
        try:
            app.obs_workflow_log(f"Silent Director direct banner error: {e}")
        except Exception:
            pass
        try:
            app.director_log_add(f"ERROR banner direct: {e}")
        except Exception:
            pass
        return False


def silent_director_scene_values(app: Any):
    scenes = [str(s).strip() for s in getattr(app.obs_workflow_state, "scenes", []) or []]
    scenes = [s for s in scenes if s and s != "No scene cache yet"]
    return [""] + scenes


def silent_director_source_values(app: Any):
    values = []
    for source in getattr(app.obs_workflow_state, "sources", []) or []:
        if isinstance(source, dict):
            name = str(source.get("name", "")).strip()
        else:
            name = str(source).strip()
        if name and name != "No source cache yet" and name not in values:
            values.append(name)
    return [""] + values


def silent_director_normalize_wait_seconds(app: Any):
    raw = str(app.silent_director_wait_seconds.get() or "").strip().replace(",", ".")
    try:
        value = float(raw)
    except Exception:
        value = 5.0
    value = max(0.1, min(300.0, value))
    if value.is_integer():
        return str(int(value))
    return f"{value:.2f}".rstrip("0").rstrip(".")


def silent_director_update_action_fields(app: Any, *_args):
    action_type = str(app.silent_director_action_type.get() or "").strip()
    frames = getattr(app, "silent_director_dynamic_frames", {}) or {}
    for frame in frames.values():
        try:
            frame.grid_remove()
        except Exception:
            pass

    key = {
        "switch_scene": "scene",
        "show_banner": "banner",
        "show_source": "source",
        "hide_source": "source",
        "wait": "wait",
    }.get(action_type)

    if key in frames:
        try:
            frames[key].grid()
        except Exception:
            pass


def silent_director_timeline_style(app: Any, action_type):
    styles = {
        "switch_scene": {
            "badge": "SC",
            "title": "SWITCH SCENE",
            "accent": "#D6B35A",
            "card": "#201D15",
        },
        "show_banner": {
            "badge": "BN",
            "title": "SHOW BANNER",
            "accent": "#77C98A",
            "card": "#162019",
        },
        "show_source": {
            "badge": "ON",
            "title": "SHOW SOURCE",
            "accent": "#E29A55",
            "card": "#241B14",
        },
        "hide_source": {
            "badge": "OFF",
            "title": "HIDE SOURCE",
            "accent": "#D77777",
            "card": "#241616",
        },
        "wait": {
            "badge": "TM",
            "title": "WAIT",
            "accent": "#6EA6E8",
            "card": "#16202C",
        },
    }
    return styles.get(
        str(action_type or "").strip(),
        {
            "badge": "AC",
            "title": str(action_type or "ACTION").upper(),
            "accent": "#AAAAAA",
            "card": "#1B1B1B",
        },
    )


def silent_director_timeline_detail(app: Any, action):
    action_type = str(action.get("type", "") or "").strip()
    if action_type == "switch_scene":
        return str(action.get("scene", "") or "-")
    if action_type == "show_banner":
        return str(action.get("text", "") or "-")
    if action_type in ("show_source", "hide_source"):
        return str(action.get("source", "") or "-")
    if action_type == "wait":
        return f"{action.get('seconds', '5')} Sekunden"
    return "-"


def silent_director_preset_stats(app: Any, preset):
    """Return action count and planned duration from WAIT actions."""
    actions = list((preset or {}).get("actions", []) or [])
    total_seconds = 0.0

    for action in actions:
        if str(action.get("type", "") or "").strip() != "wait":
            continue
        raw = str(action.get("seconds", "0") or "0").strip().replace(",", ".")
        try:
            total_seconds += max(0.0, float(raw))
        except Exception:
            pass

    return len(actions), total_seconds


def silent_director_format_duration(app: Any, total_seconds):
    try:
        total_seconds = max(0.0, float(total_seconds))
    except Exception:
        total_seconds = 0.0

    if total_seconds < 60:
        if total_seconds.is_integer():
            return f"{int(total_seconds)} s"
        return f"{total_seconds:.1f} s"

    minutes = int(total_seconds // 60)
    seconds = total_seconds - (minutes * 60)

    if seconds <= 0:
        return f"{minutes} min"
    if seconds.is_integer():
        return f"{minutes} min {int(seconds)} s"
    return f"{minutes} min {seconds:.1f} s"


def silent_director_preset_stats_text(app: Any, preset):
    action_count, total_seconds = app.silent_director_preset_stats(preset)
    action_word = "Action" if action_count == 1 else "Actions"
    return (
        f"{action_count} {action_word}  •  "
        f"Gesamtdauer {app.silent_director_format_duration(total_seconds)}"
    )


def silent_director_toggle_favorite(app: Any, preset):
    if not preset:
        return

    preset_name = str(preset.get("name", "") or "")
    for item in app.silent_director_presets:
        if str(item.get("name", "") or "") == preset_name:
            item["favorite"] = not bool(item.get("favorite", False))
            break

    silent_director.save_presets(app.silent_director_presets)
    app.obs_workflow_mark_command(
        f"Silent Director preset favorite toggled: {preset_name}"
    )
    app.show_silent_director_page()


def silent_director_toggle_favorites_filter(app: Any):
    app.silent_director_favorites_only.set(
        not bool(app.silent_director_favorites_only.get())
    )
    app.show_silent_director_page()


def silent_director_preset_icon(app: Any, preset):
    explicit = str((preset or {}).get("icon", "AUTO") or "AUTO").strip().upper()
    if explicit and explicit != "AUTO":
        return explicit

    name = str((preset or {}).get("name", "") or "").casefold()

    rules = [
        (("pause", "break", "brb"), "BRB"),
        (("podcast", "talk", "interview"), "MIC"),
        (("music", "song", "audio"), "MUS"),
        (("game", "gaming", "gameplay", "boss"), "GME"),
        (("intro", "opening", "start"), "IN"),
        (("outro", "ending", "end"), "OUT"),
        (("test", "probe", "demo"), "TST"),
        (("news", "show", "live"), "LIVE"),
    ]

    for keywords, icon in rules:
        if any(keyword in name for keyword in keywords):
            return icon

    return "PRE"


def silent_director_icon_options(app: Any):
    return [
        "AUTO",
        "PRE",
        "GME",
        "BRB",
        "MIC",
        "MUS",
        "LIVE",
        "IN",
        "OUT",
        "TST",
    ]


def silent_director_filtered_presets(app: Any):
    query = str(app.silent_director_search_var.get() or "").strip().casefold()
    presets = list(app.silent_director_presets or [])

    if bool(app.silent_director_favorites_only.get()):
        presets = [
            preset for preset in presets
            if bool(preset.get("favorite", False))
        ]

    if query:
        presets = [
            preset for preset in presets
            if query in str(preset.get("name", "") or "").casefold()
        ]

    return sorted(
        presets,
        key=lambda preset: (
            not bool(preset.get("favorite", False)),
            str(preset.get("name", "") or "").casefold(),
        ),
    )


def silent_director_clear_search(app: Any):
    app.silent_director_search_var.set("")
    app.silent_director_render_filtered_presets()
