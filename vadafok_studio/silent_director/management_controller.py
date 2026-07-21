"""Preset and action management for the Silent Director."""

from __future__ import annotations

from typing import Any
from tkinter import messagebox

from ..core import silent_director


def _name_exists(app: Any, name: str, exclude: str = "") -> bool:
    target = str(name or "").strip().casefold()
    excluded = str(exclude or "").strip().casefold()
    return any(
        str(item.get("name", "") or "").strip().casefold() == target
        and str(item.get("name", "") or "").strip().casefold() != excluded
        for item in getattr(app, "silent_director_presets", [])
    )

def reload_presets(app: Any):
    try:
        app.silent_director_presets = silent_director.load_presets()
    except Exception:
        app.silent_director_presets = []
    if app.silent_director_presets and (not app.silent_director_selected.get()):
        app.silent_director_selected.set(app.silent_director_presets[0]["name"])
    return app.silent_director_presets


def get_selected_preset(app: Any):
    name = app.silent_director_selected.get()
    for preset in app.silent_director_presets:
        if preset.get("name") == name:
            return preset
    return app.silent_director_presets[0] if app.silent_director_presets else None


def create_preset(app: Any):
    name = app.silent_director_new_name.get().strip()
    if not name:
        messagebox.showinfo("Silent Director", "Please enter a preset name.")
        return
    if _name_exists(app, name):
        messagebox.showwarning("Silent Director", f"Ein Preset namens '{name}' existiert bereits.")
        return
    scene = getattr(app.obs_workflow_state, "current_scene", "") if hasattr(app, "obs_workflow_state") else ""
    app.silent_director_presets = silent_director.add_preset(name, scene=scene, banner_text="", show_banner=False)
    app.silent_director_selected.set(name)
    app.silent_director_new_name.set("")
    app.show_silent_director_page()


def duplicate_preset(app: Any, preset=None):
    preset = preset or app.silent_director_get_selected_preset()
    if not preset:
        return

    original_name = str(preset.get("name", "") or "").strip()
    app.silent_director_presets = silent_director.duplicate_preset(original_name)

    new_name = None
    original_found = False
    for item in app.silent_director_presets:
        item_name = str(item.get("name", "") or "").strip()
        if original_found:
            new_name = item_name
            break
        if item_name == original_name:
            original_found = True

    if new_name:
        app.silent_director_selected.set(new_name)

    app.silent_director_edit_index = None
    app.silent_director_action_button_text.set("+ ADD ACTION")
    app.obs_workflow_mark_command(f"Silent Director preset duplicated: {original_name}")
    app.show_silent_director_page()


def delete_selected_preset(app: Any):
    preset = app.silent_director_get_selected_preset()
    if not preset:
        return
    name = preset.get("name", "")
    if not messagebox.askyesno("Silent Director", f"Delete preset '{name}'?"):
        return
    app.silent_director_presets = silent_director.delete_preset(name)
    app.silent_director_selected.set(app.silent_director_presets[0]["name"] if app.silent_director_presets else "")
    app.show_silent_director_page()


def load_editor(app: Any, preset):
    if not preset:
        return
    app.silent_director_editor_name.set(preset.get("name", "Untitled"))
    app.silent_director_editor_icon.set(
        str(preset.get("icon", "AUTO") or "AUTO").upper()
    )
    app.silent_director_editor_scene.set(preset.get("scene", ""))
    app.silent_director_editor_show_banner.set(bool(preset.get("show_banner", False)))


def save_selected_preset(app: Any):
    preset = app.silent_director_get_selected_preset()
    if not preset:
        return

    old_name = preset.get("name", "")
    new_name = app.silent_director_editor_name.get().strip()
    if not new_name:
        messagebox.showinfo("Silent Director", "Preset name darf nicht leer sein.")
        return
    if _name_exists(app, new_name, exclude=old_name):
        messagebox.showwarning(
            "Silent Director", f"Ein Preset namens '{new_name}' existiert bereits.",
        )
        return

    banner_text = ""
    try:
        banner_text = app.silent_director_banner_textbox.get("1.0", "end").strip()
    except Exception:
        banner_text = preset.get("banner_text", "")

    updated = {
        "name": new_name,
        "icon": str(app.silent_director_editor_icon.get() or "AUTO").strip().upper(),
        "scene": app.silent_director_editor_scene.get().strip(),
        "banner_text": banner_text,
        "show_banner": bool(app.silent_director_editor_show_banner.get()),
        "show_sources": list(preset.get("show_sources", []) or []),
        "hide_sources": list(preset.get("hide_sources", []) or []),
        "actions": list(preset.get("actions", []) or []),
    }

    app.silent_director_presets = silent_director.update_preset(old_name, updated)
    app.silent_director_selected.set(new_name)
    app.obs_workflow_mark_command(f"Silent Director preset saved: {new_name}")
    messagebox.showinfo("Silent Director", f"Preset '{new_name}' gespeichert.")
    app.show_silent_director_page()


def cancel_action_edit(app: Any):
    app.silent_director_edit_index = None
    app.silent_director_action_button_text.set("+ ADD ACTION")
    app.silent_director_action_type.set("switch_scene")
    app.silent_director_action_scene.set("")
    app.silent_director_action_source.set("")
    app.silent_director_action_text.set("")
    app.silent_director_wait_seconds.set("5")
    app.silent_director_update_action_fields()


def edit_action(app: Any, index):
    preset = app.silent_director_get_selected_preset()
    if not preset:
        return
    actions = list(preset.get("actions", []) or [])
    if not (0 <= index < len(actions)):
        return

    action = actions[index]
    app.silent_director_edit_index = index
    app.silent_director_action_button_text.set("UPDATE ACTION")
    app.silent_director_action_type.set(str(action.get("type", "switch_scene")))
    app.silent_director_action_scene.set(str(action.get("scene", "")))
    app.silent_director_action_source.set(str(action.get("source", "")))
    app.silent_director_action_text.set(str(action.get("text", "")))
    app.silent_director_wait_seconds.set(str(action.get("seconds", "5") or "5"))
    app.silent_director_update_action_fields()


def duplicate_action(app: Any, index):
    preset = app.silent_director_get_selected_preset()
    if not preset:
        return

    actions = list(preset.get("actions", []) or [])
    if not (0 <= index < len(actions)):
        return

    app.silent_director_presets = silent_director.duplicate_action(
        preset.get("name", ""),
        index
    )

    # Select the new copy immediately for fast editing.
    app.silent_director_edit_index = index + 1
    app.silent_director_action_button_text.set("UPDATE ACTION")

    updated_preset = app.silent_director_get_selected_preset()
    updated_actions = list(updated_preset.get("actions", []) or []) if updated_preset else []
    if 0 <= index + 1 < len(updated_actions):
        action = updated_actions[index + 1]
        app.silent_director_action_type.set(str(action.get("type", "switch_scene")))
        app.silent_director_action_scene.set(str(action.get("scene", "")))
        app.silent_director_action_source.set(str(action.get("source", "")))
        app.silent_director_action_text.set(str(action.get("text", "")))
        app.silent_director_wait_seconds.set(str(action.get("seconds", "5") or "5"))
        app.silent_director_update_action_fields()

    app.obs_workflow_mark_command("Silent Director action duplicated")
    app.silent_director_render_actions_list()


def move_action(app: Any, index, direction):
    preset = app.silent_director_get_selected_preset()
    if not preset:
        return
    app.silent_director_presets = silent_director.move_action(
        preset.get("name", ""), index, direction
    )
    app.silent_director_edit_index = None
    app.silent_director_action_button_text.set("+ ADD ACTION")
    app.obs_workflow_mark_command("Silent Director action moved")
    app.silent_director_render_actions_list()


def add_action(app: Any):
    preset = app.silent_director_get_selected_preset()
    if not preset:
        return

    action_type = app.silent_director_action_type.get()
    action = {
        "type": action_type,
        "scene": "",
        "text": "",
        "source": "",
        "seconds": "",
    }

    if action_type == "switch_scene":
        action["scene"] = app.silent_director_action_scene.get().strip()
        if not action["scene"]:
            messagebox.showinfo("Silent Director", "Bitte eine Szene wählen.")
            return

    elif action_type == "show_banner":
        action["text"] = app.silent_director_action_text.get().strip()
        if not action["text"]:
            messagebox.showinfo("Silent Director", "Bitte einen Bannertext eingeben.")
            return

    elif action_type in ("show_source", "hide_source"):
        action["source"] = app.silent_director_action_source.get().strip()
        if not action["source"]:
            messagebox.showinfo("Silent Director", "Bitte eine Source wählen.")
            return

    elif action_type == "wait":
        action["seconds"] = app.silent_director_normalize_wait_seconds()

    if app.silent_director_edit_index is None:
        app.silent_director_presets = silent_director.add_action(
            preset.get("name", ""), action
        )
        command_text = f"Silent Director action added: {action_type}"
    else:
        app.silent_director_presets = silent_director.update_action(
            preset.get("name", ""),
            app.silent_director_edit_index,
            action,
        )
        command_text = f"Silent Director action updated: {action_type}"

    app.silent_director_edit_index = None
    app.silent_director_action_button_text.set("+ ADD ACTION")
    app.silent_director_action_text.set("")
    app.silent_director_wait_seconds.set("5")
    app.obs_workflow_mark_command(command_text)
    app.silent_director_cancel_action_edit()
    app.silent_director_render_actions_list()


def delete_action(app: Any, index):
    preset = app.silent_director_get_selected_preset()
    if not preset:
        return
    app.silent_director_presets = silent_director.delete_action(preset.get("name", ""), index)
    app.silent_director_edit_index = None
    app.silent_director_action_button_text.set("+ ADD ACTION")
    app.obs_workflow_mark_command("Silent Director action deleted")
    app.silent_director_render_actions_list()
