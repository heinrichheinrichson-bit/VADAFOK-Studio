"""Preset execution for the Silent Director."""

from __future__ import annotations

import time
from typing import Any
from tkinter import messagebox


def run_preset(app: Any, preset: dict | None = None) -> None:
    """Execute one Silent Director preset against the connected OBS session."""
    if preset is None:
        preset = app.silent_director_get_selected_preset()
    if not preset:
        messagebox.showinfo("Silent Director", "No preset selected.")
        return

    name = preset.get("name", "Untitled")
    actions = list(preset.get("actions", []) or [])

    if not actions:
        scene = str(preset.get("scene", "") or "").strip()
        banner_text = str(preset.get("banner_text", "") or "").strip()
        show_banner = bool(preset.get("show_banner", False))
        show_sources = list(preset.get("show_sources", []) or [])
        hide_sources = list(preset.get("hide_sources", []) or [])

        if scene:
            actions.append({"type": "switch_scene", "scene": scene, "text": "", "source": ""})
        if show_banner and banner_text:
            actions.append({"type": "show_banner", "scene": "", "text": banner_text, "source": ""})
        for source in show_sources:
            actions.append({"type": "show_source", "scene": "", "text": "", "source": source})
        for source in hide_sources:
            actions.append({"type": "hide_source", "scene": "", "text": "", "source": source})

    if not actions:
        app.director_set_status("READY", "No actions", "0 / 0")
        messagebox.showinfo("Silent Director", f"Preset '{name}' enthält noch keine ausführbaren Aktionen.")
        return

    if not app.ensure_obs_ready():
        app.director_set_status("ERROR", "OBS not connected", "0 / 0")
        return

    app.director_stop_requested = False
    app.director_clear_active_action()
    total = len(actions)
    app.director_set_status("RUNNING", f"Preset: {name}", f"0 / {total}")
    app.director_log_add(f"RUN Preset '{name}' started ({total} action(s))")

    try:
        actions_done = []

        for idx, action in enumerate(actions, start=1):
            if app.director_stop_requested:
                app.director_set_status("STOPPED", "Stopped by user", f"{idx-1} / {total}")
                app.director_log_add("STOPPED by user")
                app.director_clear_active_action()
                return

            action_type = action.get("type", "")
            label = app.director_action_label(action)
            app.director_set_active_action(idx - 1)
            app.director_set_status("RUNNING", label, f"{idx} / {total}")
            app.director_log_add(f"{idx}/{total} {label}")

            if action_type == "switch_scene":
                scene = str(action.get("scene", "")).strip()
                if scene:
                    app.obs.switch_scene(scene)
                    app.obs_workflow_state.current_scene = scene
                    app.obs_workflow_state.last_scene_switch = scene
                    try:
                        app.obs_workflow_state.last_scene_switch_time = app.obs_workflow_state.now()
                    except Exception:
                        app.obs_workflow_state.last_scene_switch_time = ""
                    actions_done.append(f"Scene -> {scene}")

            elif action_type == "show_banner":
                text = str(action.get("text", "")).strip()
                if text:
                    try:
                        ok = app.silent_director_show_banner_direct(text)
                        if ok:
                            actions_done.append(f"Banner -> {text}")
                        else:
                            actions_done.append(f"Banner failed -> {text}")
                    except Exception as e:
                        app.obs_workflow_log(f"Silent Director banner error: {e}")
                        app.director_log_add(f"ERROR banner: {e}")

            elif action_type == "wait":
                raw_seconds = str(action.get("seconds", "5") or "5").strip().replace(",", ".")
                try:
                    seconds = float(raw_seconds)
                except Exception:
                    seconds = 5.0
                seconds = max(0.1, min(300.0, seconds))

                app.director_set_status(
                    "WAITING",
                    f"WAIT {seconds:g} s",
                    f"{idx} / {total}"
                )
                app.director_log_add(f"WAIT {seconds:g} s")

                deadline = time.monotonic() + seconds
                while time.monotonic() < deadline:
                    if app.director_stop_requested:
                        app.director_set_status(
                            "STOPPED",
                            "Stopped during WAIT",
                            f"{idx-1} / {total}"
                        )
                        app.director_log_add("STOPPED during WAIT")
                        app.director_clear_active_action()
                        return

                    remaining = max(0.0, deadline - time.monotonic())
                    app.director_current_action_var.set(
                        f"WAIT {remaining:.1f} s"
                    )

                    try:
                        app.update()
                    except Exception:
                        pass
                    time.sleep(0.05)

                app.director_log_add("WAIT finished")
                actions_done.append(f"WAIT -> {seconds:g} s")
                app.director_set_status(
                    "RUNNING",
                    label,
                    f"{idx} / {total}"
                )

            elif action_type == "show_source":
                source = str(action.get("source", "")).strip()
                if source:
                    app.obs_workflow_set_source_visibility(source, True)
                    actions_done.append(f"SHOW Source -> {source}")

            elif action_type == "hide_source":
                source = str(action.get("source", "")).strip()
                if source:
                    app.obs_workflow_set_source_visibility(source, False)
                    actions_done.append(f"HIDE Source -> {source}")

        if hasattr(app.obs_workflow_state, "add_event"):
            app.obs_workflow_state.add_event(f"Silent Director: {name}")
        app.obs_workflow_mark_command(f"Silent Director: {name}")
        app.director_set_status("FINISHED", "Finished", f"{total} / {total}")
        app.director_log_add(f"FINISHED Preset '{name}'")
        app.director_clear_active_action()

        try:
            app.obs_workflow_refresh(silent=True)
        except Exception:
            pass
        # No full page redraw here; textvariables update the monitor live.

    except Exception as e:
        app.director_clear_active_action()
        app.director_set_status("ERROR", str(e), app.director_progress_var.get())
        app.director_log_add(f"ERROR {e}")
        app.obs_workflow_log(f"SILENT DIRECTOR ERROR: {e}")
        messagebox.showerror("Silent Director", str(e))
