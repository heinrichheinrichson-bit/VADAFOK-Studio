"""OBS Workflow behavior controller.

This module owns the existing OBS workflow orchestration while UI widgets,
configuration variables, and runtime state remain on the application object.
The split is intentionally behavior-preserving.
"""

from __future__ import annotations

from tkinter import messagebox

from ..core.obs_controller import OBSController
from ..core import obs_workflow, scene_favorites

GOLD = "#D6A43A"
TEXT = "#F2E2B6"


class OBSWorkflowController:
    """Coordinate OBS workflow actions for one application instance."""

    def __init__(self, app):
        self.app = app

    def obs_workflow_set_sidebar_status(self, connected):
        app = self.app
        try:
            label = getattr(app, "status_label", None)
            if label is not None:
                if connected:
                    label.configure(text="● Connected", text_color="#6EE08C")
                else:
                    label.configure(text="● Not connected", text_color="#D86A6A")
        except Exception:
            pass



    def obs_workflow_log(self, message):
        app = self.app
        if not hasattr(app, "obs_workflow_state"):
            app.obs_workflow_state = obs_workflow.OBSWorkflowState()
        app.obs_workflow_state.add_log(str(message))


    def obs_workflow_mark_command(self, message):
        app = self.app
        if not hasattr(app, "obs_workflow_state"):
            app.obs_workflow_state = obs_workflow.OBSWorkflowState()
        app.obs_workflow_state.command(str(message))


    def obs_workflow_is_connected(self):
        app = self.app
        obs_obj = getattr(app, "obs", None)
        if obs_obj is None:
            return False
        try:
            probe = getattr(obs_obj, "probe", None)
            if callable(probe):
                return bool(probe())
            return bool(obs_obj.is_connected())
        except Exception:
            return False



    def obs_workflow_connect(self):
        app = self.app
        connected_after_probe = False

        try:
            app.connect_obs()

            try:
                connected_after_probe = self.obs_workflow_is_connected()
            except Exception:
                connected_after_probe = False

            if hasattr(app.obs_workflow_state, "set_connected"):
                app.obs_workflow_state.set_connected(connected_after_probe)
            else:
                app.obs_workflow_state.connected = connected_after_probe

            self.obs_workflow_set_sidebar_status(connected_after_probe)

            if connected_after_probe:
                app.obs_workflow_state.last_error = ""
                if hasattr(app.obs_workflow_state, "add_event"):
                    app.obs_workflow_state.add_event("OBS connected")
                self.obs_workflow_mark_command("OBS connected")
                self.obs_workflow_refresh(silent=True)
            else:
                app.obs_workflow_state.last_error = "OBS probe failed after connect"
                self.obs_workflow_log("CONNECT ERROR: OBS probe failed after connect")
                messagebox.showerror("OBS Workflow", "OBS Verbindung wurde aufgebaut, aber die Statusprüfung ist fehlgeschlagen.")

        except Exception as e:
            try:
                if hasattr(app.obs_workflow_state, "set_connected"):
                    app.obs_workflow_state.set_connected(False)
                else:
                    app.obs_workflow_state.connected = False
            except Exception:
                pass
            self.obs_workflow_set_sidebar_status(False)
            app.obs_workflow_state.last_error = str(e)
            self.obs_workflow_log(f"CONNECT ERROR: {e}")
            messagebox.showerror("OBS Workflow", str(e))

        app.show_obs_workflow_page()



    def obs_workflow_disconnect(self):
        app = self.app
        try:
            obs_obj = getattr(app, "obs", None)
            if obs_obj is not None:
                try:
                    obs_obj.disconnect()
                except Exception:
                    pass

            # Replace controller instance to guarantee no stale websocket/client is reused.
            app.obs = OBSController()

            if hasattr(app.obs_workflow_state, "set_connected"):
                app.obs_workflow_state.set_connected(False)
            else:
                app.obs_workflow_state.connected = False

            self.obs_workflow_set_sidebar_status(False)
            app.obs_workflow_state.last_error = ""

            if hasattr(app.obs_workflow_state, "add_event"):
                app.obs_workflow_state.add_event("OBS disconnected")
            self.obs_workflow_mark_command("OBS disconnected")

        except Exception as e:
            try:
                app.obs = OBSController()
            except Exception:
                pass
            try:
                app.obs_workflow_state.set_connected(False)
            except Exception:
                app.obs_workflow_state.connected = False
            self.obs_workflow_set_sidebar_status(False)
            app.obs_workflow_state.last_error = str(e)
            self.obs_workflow_log(f"DISCONNECT ERROR: {e}")
            messagebox.showerror("OBS Workflow", str(e))

        app.show_obs_workflow_page()



    def obs_workflow_refresh(self, silent=False):
        app = self.app
        if not hasattr(app, "obs_workflow_state"):
            app.obs_workflow_state = obs_workflow.OBSWorkflowState()

        connected_now = self.obs_workflow_is_connected()
        if not connected_now:
            self.obs_workflow_log("OBS probe failed / disconnected")
        self.obs_workflow_set_sidebar_status(connected_now)
        if hasattr(app.obs_workflow_state, "set_connected"):
            app.obs_workflow_state.set_connected(connected_now)
        else:
            app.obs_workflow_state.connected = connected_now

        scenes = []
        sources = []

        try:
            obs = getattr(app, "obs", None)
            if obs is not None and connected_now:
                # Scene cache
                try:
                    if hasattr(obs, "get_scene_list"):
                        scenes = obs.get_scene_list()
                    else:
                        for method_name in ("get_scenes", "list_scenes"):
                            method = getattr(obs, method_name, None)
                            if callable(method):
                                result = method()
                                if isinstance(result, list):
                                    scenes = [str(x.get("sceneName", x)) if isinstance(x, dict) else str(x) for x in result]
                                elif isinstance(result, dict):
                                    raw = result.get("scenes", [])
                                    scenes = [str(x.get("sceneName", x)) if isinstance(x, dict) else str(x) for x in raw]
                                break
                except Exception as scene_error:
                    self.obs_workflow_log(f"SCENE CACHE ERROR: {scene_error}")

                try:
                    if hasattr(obs, "get_current_scene_name"):
                        app.obs_workflow_state.current_scene = obs.get_current_scene_name()
                    else:
                        app.obs_workflow_state.current_scene = obs.current_scene("")
                except Exception:
                    app.obs_workflow_state.current_scene = ""

                # Source cache for current scene
                try:
                    if hasattr(obs, "get_scene_sources"):
                        sources = obs.get_scene_sources(getattr(app.obs_workflow_state, "current_scene", ""))
                    else:
                        for method_name in ("get_sources", "list_sources", "get_source_list", "get_scene_items"):
                            method = getattr(obs, method_name, None)
                            if callable(method):
                                result = method()
                                if isinstance(result, list):
                                    sources = [str(x.get("sourceName", x.get("inputName", x))) if isinstance(x, dict) else str(x) for x in result]
                                elif isinstance(result, dict):
                                    raw = result.get("sources", result.get("inputs", result.get("sceneItems", [])))
                                    sources = [str(x.get("sourceName", x.get("inputName", x))) if isinstance(x, dict) else str(x) for x in raw]
                                break
                except Exception as source_error:
                    self.obs_workflow_log(f"SOURCE CACHE ERROR: {source_error}")
        except Exception as e:
            if hasattr(app.obs_workflow_state, "set_connected"):
                app.obs_workflow_state.set_connected(False)
            else:
                app.obs_workflow_state.connected = False
            app.obs_workflow_state.last_error = str(e)
            self.obs_workflow_log(f"REFRESH ERROR: {e}")

        if not scenes:
            scene_value = ""
            try:
                scene_value = app.scene_name.get()
            except Exception:
                scene_value = ""
            scenes = [scene_value] if scene_value else ["No scene cache yet"]

        if not sources:
            possible = []
            for attr in ("caption_group", "caption_text", "caption_banner_source", "caption_render_source", "scene_card_source"):
                var = getattr(app, attr, None)
                if var is not None:
                    try:
                        val = var.get()
                        if val:
                            possible.append(val)
                    except Exception:
                        pass
            sources = possible or ["No source cache yet"]

        app.obs_workflow_state.scenes = scenes
        app.obs_workflow_state.sources = sources
        if scenes and scenes != ["No scene cache yet"]:
            self.obs_workflow_log(f"Scene Cache updated: {len(scenes)} scene(s) loaded")
        self.obs_workflow_mark_command("OBS cache refreshed")
        if hasattr(app.obs_workflow_state, "add_event"):
            app.obs_workflow_state.add_event("OBS cache refreshed")

        if not silent:
            app.show_obs_workflow_page()



    def obs_workflow_banner_action(self, action, text=""):
        app = self.app
        if not hasattr(app, "obs_workflow_state"):
            app.obs_workflow_state = obs_workflow.OBSWorkflowState()
        app.obs_workflow_state.set_connected(self.obs_workflow_is_connected()) if hasattr(app.obs_workflow_state, 'set_connected') else setattr(app.obs_workflow_state, 'connected', self.obs_workflow_is_connected())
        try:
            app.obs_workflow_state.banner(str(action), str(text or ""))
        except Exception:
            self.obs_workflow_mark_command(str(action))


    def obs_workflow_current_live_text(self):
        app = self.app
        try:
            if hasattr(app, "live_card_get_message_text"):
                return app.live_card_get_message_text()
        except Exception:
            pass
        try:
            if hasattr(app, "message_box"):
                return app.message_box.get("1.0", "end").strip()
        except Exception:
            pass
        return ""




    def obs_workflow_load_scene_favorites(self):
        app = self.app
        try:
            app.scene_favorites = scene_favorites.load_favorites()
        except Exception:
            app.scene_favorites = []
        return app.scene_favorites


    def obs_workflow_add_scene_favorite(self, scene_name):
        app = self.app
        scene_name = str(scene_name or "").strip()
        if not scene_name or scene_name == "No scene cache yet":
            return
        app.scene_favorites = scene_favorites.add_favorite(scene_name)
        self.obs_workflow_log(f"Scene favorite added: {scene_name}")
        app.show_obs_workflow_page()


    def obs_workflow_remove_scene_favorite(self, scene_name):
        app = self.app
        scene_name = str(scene_name or "").strip()
        if not scene_name:
            return
        app.scene_favorites = scene_favorites.remove_favorite(scene_name)
        self.obs_workflow_log(f"Scene favorite removed: {scene_name}")
        app.show_obs_workflow_page()


    def obs_workflow_update_scene_ui(self):
        """Update OBS Workflow scene indicators without rebuilding the full page."""
        app = self.app
        state = getattr(app, "obs_workflow_state", None)
        if state is None:
            return

        current_scene = getattr(state, "current_scene", "") or "Unknown"
        last_switch = getattr(state, "last_scene_switch", "") or "-"
        last_time = getattr(state, "last_scene_switch_time", "") or ""

        last_text = last_switch + (f"  {last_time}" if last_time else "")
        last_control = f"Last Scene Switch: {last_switch}"
        if last_time:
            last_control += f" at {last_time}"

        try:
            app.obs_workflow_current_scene_var.set(current_scene)
            app.obs_workflow_last_switch_var.set(last_text)
            app.obs_workflow_live_scene_var.set(f"LIVE SCENE  {current_scene}")
            app.obs_workflow_last_scene_control_var.set(last_control)
        except Exception:
            pass

        try:
            buttons = getattr(app, "obs_workflow_favorite_buttons", {}) or {}
            for scene_name, button in buttons.items():
                active = scene_name == current_scene
                button.configure(
                    fg_color=GOLD if active else "#171717",
                    text_color="#111111" if active else "#D9C58C",
                )
        except Exception:
            pass

        try:
            rows = getattr(app, "obs_workflow_scene_rows", {}) or {}
            for scene_name, widgets in rows.items():
                active = scene_name == current_scene
                row = widgets.get("row")
                label = widgets.get("label")
                switch = widgets.get("switch")

                if row is not None:
                    row.configure(
                        fg_color="#171717" if active else "transparent",
                    )
                if label is not None:
                    label.configure(
                        text=f"● LIVE  {scene_name}" if active else scene_name,
                        text_color="#8FE6A0" if active else TEXT,
                    )
                if switch is not None:
                    switch.configure(
                        fg_color="#333333" if active else GOLD,
                        text_color="#AAAAAA" if active else "#111111",
                    )
        except Exception:
            pass

        try:
            app.update_idletasks()
        except Exception:
            pass



    def obs_workflow_switch_scene(self, scene_name):
        app = self.app
        scene_name = str(scene_name or "").strip()
        if not scene_name or scene_name == "No scene cache yet":
            return

        if not app.ensure_obs_ready():
            return

        try:
            app.obs.switch_scene(scene_name)
            app.obs_workflow_state.current_scene = scene_name
            app.obs_workflow_state.last_scene_switch = scene_name
            try:
                app.obs_workflow_state.last_scene_switch_time = app.obs_workflow_state.now()
            except Exception:
                app.obs_workflow_state.last_scene_switch_time = ""

            if hasattr(app.obs_workflow_state, "add_event"):
                app.obs_workflow_state.add_event(f"Scene switched: {scene_name}")
            self.obs_workflow_mark_command(f"Scene switched: {scene_name}")

            try:
                active_scene = app.current_scene()
                if active_scene:
                    app.obs_workflow_state.current_scene = active_scene
            except Exception:
                pass

            self.obs_workflow_update_scene_ui()

        except Exception as e:
            app.obs_workflow_state.last_error = str(e)
            self.obs_workflow_log(f"SCENE SWITCH ERROR: {e}")
            messagebox.showerror("Scene Switch", str(e))
            # Keep the current page visible even on error.



    def obs_workflow_refresh_sources_only(self):
        """Refresh only the source list for the current scene, without rebuilding scene cache."""
        app = self.app
        try:
            if not self.obs_workflow_is_connected():
                return False

            scene = getattr(app.obs_workflow_state, "current_scene", "") or app.current_scene()
            if hasattr(app.obs, "get_scene_sources"):
                app.obs_workflow_state.sources = app.obs.get_scene_sources(scene)
                return True
        except Exception as e:
            app.obs_workflow_state.last_error = str(e)
            self.obs_workflow_log(f"SOURCE REFRESH ERROR: {e}")
        return False



    def obs_workflow_update_source_row_ui(self, source_name, enabled):
        """Update only one rendered source row, without rebuilding the whole OBS Workflow page."""
        app = self.app
        try:
            widgets = getattr(app, "obs_source_row_widgets", {}).get(source_name)
            if not widgets:
                return False

            label = widgets.get("label")
            show_btn = widgets.get("show_btn")
            hide_btn = widgets.get("hide_btn")

            label_text = ("✓ " if enabled else "✗ ") + source_name
            label_color = "#8FE6A0" if enabled else "#F08A8A"

            if label is not None:
                label.configure(text=label_text, text_color=label_color)

            if show_btn is not None:
                show_btn.configure(
                    fg_color=GOLD if not enabled else "#333333",
                    text_color="#111111" if not enabled else "#AAAAAA"
                )

            if hide_btn is not None:
                hide_btn.configure(
                    fg_color="#5A1F1F" if enabled else "#333333",
                    text_color="#FFFFFF" if enabled else "#AAAAAA"
                )

            return True
        except Exception:
            return False


    def obs_workflow_set_source_visibility(self, source_name, enabled):
        app = self.app
        source_name = str(source_name or "").strip()
        if not source_name:
            return
        if not app.ensure_obs_ready():
            return

        try:
            scene = getattr(app.obs_workflow_state, "current_scene", "") or app.current_scene()
            app.obs.set_source_visibility(scene, source_name, enabled)

            # Update local source cache.
            for source in getattr(app.obs_workflow_state, "sources", []):
                if isinstance(source, dict) and source.get("name") == source_name:
                    source["enabled"] = bool(enabled)
                    break

            action = "SHOW Source" if enabled else "HIDE Source"
            if hasattr(app.obs_workflow_state, "add_event"):
                app.obs_workflow_state.add_event(f"{action}: {source_name}")
            self.obs_workflow_mark_command(f"{action}: {source_name}")

            # True no-flicker update: only touch the affected row.
            self.obs_workflow_update_source_row_ui(source_name, bool(enabled))

        except Exception as e:
            app.obs_workflow_state.last_error = str(e)
            self.obs_workflow_log(f"SOURCE VISIBILITY ERROR: {e}")
            messagebox.showerror("Source Manager", str(e))




    def obs_workflow_required_overlay_sources(self):
        app = self.app
        names = []
        for attr in ("caption_group", "caption_text", "caption_banner_source", "caption_render_source", "scene_card_source"):
            var = getattr(app, attr, None)
            if var is not None:
                try:
                    value = str(var.get()).strip()
                    if value and value not in names:
                        names.append(value)
                except Exception:
                    pass
        return names


    def obs_workflow_normalize_source_name(self, name):
        app = self.app
        base = " ".join(str(name or "").strip().lower().split())

        # Remove pure numeric suffix without requiring a regex import.
        # Examples:
        # "vadafok caption 2" -> "vadafok caption"
        # "vadafok caption2"  -> "vadafok caption"
        parts = base.split()
        if parts and parts[-1].isdigit():
            base = " ".join(parts[:-1]).strip()

        while base and base[-1].isdigit():
            base = base[:-1].strip()

        return base



    def obs_workflow_source_matches(self, required_name, found_names):
        app = self.app
        required_norm = self.obs_workflow_normalize_source_name(required_name)
        for found_name in found_names:
            found_norm = self.obs_workflow_normalize_source_name(found_name)

            if found_norm == required_norm:
                return True

            # Allow exact duplicate suffix variants:
            # "VADAFOK Caption1" -> "VADAFOK Caption"
            if found_norm.startswith(required_norm) and found_norm[len(required_norm):].strip().isdigit():
                return True

            # Allow OBS/group variants that include the configured name, but avoid matching
            # the broad group "VADAFOK Caption" against "VADAFOK Caption Text".
            if required_norm in found_norm:
                extra = found_norm.replace(required_norm, "").strip()
                if not extra or extra.isdigit() or extra in ("group", "grp"):
                    return True

        return False


    def obs_workflow_scan_overlay_health(self, silent=False):
        app = self.app
        if not app.ensure_obs_ready():
            return

        required = self.obs_workflow_required_overlay_sources()
        if not required:
            messagebox.showinfo("Overlay Health", "Keine VADAFOK Overlay-Quellen konfiguriert.")
            return

        scenes = list(getattr(app.obs_workflow_state, "scenes", []) or [])
        scenes = [str(s).strip() for s in scenes if s and str(s).strip() != "No scene cache yet"]

        if not scenes:
            try:
                scenes = app.obs.get_scene_list()
                app.obs_workflow_state.scenes = scenes
            except Exception as e:
                app.obs_workflow_state.last_error = str(e)
                messagebox.showerror("Overlay Health", str(e))
                return

        results = []
        ok_count = 0

        for scene in scenes:
            try:
                if hasattr(app.obs, "get_scene_sources_recursive"):
                    sources = app.obs.get_scene_sources_recursive(scene)
                else:
                    sources = app.obs.get_scene_sources(scene)
                source_names = []
                for source in sources:
                    if isinstance(source, dict):
                        source_names.append(str(source.get("name", "")).strip())
                    else:
                        source_names.append(str(source).strip())
                source_names = [name for name in source_names if name]

                missing = []
                present = []
                for required_name in required:
                    if self.obs_workflow_source_matches(required_name, source_names):
                        present.append(required_name)
                    else:
                        missing.append(required_name)

                ok = len(missing) == 0
                if ok:
                    ok_count += 1

                # Detailed debug for this phase. Shows real OBS names.
                found_preview = ", ".join(source_names[:30])
                if len(source_names) > 30:
                    found_preview += f", ... (+{len(source_names) - 30})"
                self.obs_workflow_log(
                    f"Overlay Recursive Found [{scene}]: {found_preview}"
                )

                results.append({
                    "scene": scene,
                    "ok": ok,
                    "missing": missing,
                    "present": present,
                    "found": source_names,
                })

            except Exception as e:
                results.append({
                    "scene": scene,
                    "ok": False,
                    "missing": list(required),
                    "present": [],
                    "found": [],
                    "error": str(e),
                })
                self.obs_workflow_log(f"Overlay Scan ERROR [{scene}]: {e}")

        total = len(results)
        score = f"{ok_count} / {total} Scenes Ready" if total else "No scenes checked"

        app.obs_workflow_state.overlay_health = results
        app.obs_workflow_state.overlay_health_score = score

        issues = total - ok_count
        if hasattr(app.obs_workflow_state, "add_event"):
            app.obs_workflow_state.add_event(f"Overlay Health Scan: {total} scenes checked, {issues} issue(s)")
        self.obs_workflow_mark_command(f"Overlay Health Scan: {score}")

        if not silent:
            app.show_obs_workflow_page()




    def obs_workflow_health_counts(self):
        app = self.app
        results = getattr(app.obs_workflow_state, "overlay_health", []) or []
        if not results:
            return 0, 0, 0
        ready = sum(1 for item in results if item.get("ok"))
        total = len(results)
        return ready, total - ready, total


    def obs_workflow_current_scene_health(self):
        app = self.app
        current = getattr(app.obs_workflow_state, "current_scene", "")
        for item in getattr(app.obs_workflow_state, "overlay_health", []) or []:
            if item.get("scene") == current:
                return item
        return None


    def obs_workflow_recent_activity(self):
        app = self.app
        items = []
        for attr in ("obs_events", "banner_history", "log"):
            try:
                items.extend(getattr(app.obs_workflow_state, attr, [])[-5:])
            except Exception:
                pass
        cleaned = []
        seen = set()
        for item in items[-12:]:
            text = str(item)
            if text not in seen:
                cleaned.append(text)
                seen.add(text)
        return cleaned[-8:]




    def obs_workflow_format_activity(self, text):
        app = self.app
        text = str(text or "").strip()
        icon = "•"
        label = text

        lower = text.lower()
        if "scene switched" in lower:
            icon = "SCENE"
        elif "show live card" in lower or "hide live card" in lower:
            icon = "CARD"
        elif "show source" in lower or "hide source" in lower:
            icon = "SOURCE"
        elif "connected" in lower or "disconnect" in lower:
            icon = "OBS"
        elif "overlay" in lower:
            icon = "HEALTH"

        return f"{icon}  {label}"



    def obs_workflow_overlay_installer_source_values(self):
        app = self.app
        scenes = [str(s).strip() for s in getattr(app.obs_workflow_state, "scenes", []) or []]
        scenes = [s for s in scenes if s and s != "No scene cache yet"]
        return scenes or ["No scenes loaded"]


    def obs_workflow_overlay_installer_set_source(self, scene_name):
        app = self.app
        scene_name = str(scene_name or "").strip()
        if scene_name and scene_name != "No scenes loaded":
            app.obs_workflow_state.overlay_installer_source_scene = scene_name
            self.obs_workflow_mark_command(f"Overlay Installer source scene: {scene_name}")
        app.show_obs_workflow_page()


    def obs_workflow_overlay_installer_toggle_scene(self, scene_name):
        app = self.app
        scene_name = str(scene_name or "").strip()
        if not scene_name:
            return
        selected = list(getattr(app.obs_workflow_state, "overlay_installer_selected_scenes", []) or [])
        if scene_name in selected:
            selected.remove(scene_name)
        else:
            selected.append(scene_name)
        app.obs_workflow_state.overlay_installer_selected_scenes = selected
        app.show_obs_workflow_page()


    def obs_workflow_overlay_installer_select_missing(self):
        app = self.app
        results = getattr(app.obs_workflow_state, "overlay_health", []) or []
        selected = []
        source_scene = getattr(app.obs_workflow_state, "overlay_installer_source_scene", "")
        for item in results:
            scene = item.get("scene", "")
            if scene and not item.get("ok") and scene != source_scene:
                selected.append(scene)
        app.obs_workflow_state.overlay_installer_selected_scenes = selected
        self.obs_workflow_mark_command(f"Overlay Installer selected missing: {len(selected)} scene(s)")
        app.show_obs_workflow_page()


    def obs_workflow_overlay_installer_clear_selection(self):
        app = self.app
        app.obs_workflow_state.overlay_installer_selected_scenes = []
        self.obs_workflow_mark_command("Overlay Installer selection cleared")
        app.show_obs_workflow_page()


    def obs_workflow_overlay_installer_install_selected(self):
        app = self.app
        if not app.ensure_obs_ready():
            return

        source_scene = str(getattr(app.obs_workflow_state, "overlay_installer_source_scene", "") or "").strip()
        targets = list(getattr(app.obs_workflow_state, "overlay_installer_selected_scenes", []) or [])
        required = self.obs_workflow_required_overlay_sources()

        if not source_scene or source_scene == "No scenes loaded":
            messagebox.showinfo("Overlay Installer", "Bitte zuerst eine Source Scene wählen.")
            return

        if not targets:
            messagebox.showinfo("Overlay Installer", "Bitte zuerst Ziel-Szenen auswählen.")
            return

        if not required:
            messagebox.showinfo("Overlay Installer", "Keine VADAFOK Overlay-Quellen konfiguriert.")
            return

        confirm = messagebox.askyesno(
            "Overlay Installer",
            f"Overlay aus '{source_scene}' in {len(targets)} Szene(n) installieren?\n\nEs werden nur fehlende Quellen ergänzt. Bestehende Quellen werden nicht gelöscht oder überschrieben."
        )
        if not confirm:
            return

        successes = 0
        total_installed = 0
        total_errors = 0
        summaries = []

        for target in targets:
            try:
                result = app.obs.install_overlay_sources(source_scene, target, required)
                installed = result.get("installed", [])
                errors = result.get("errors", [])
                skipped = result.get("skipped", [])

                if installed or not errors:
                    successes += 1
                total_installed += len(installed)
                total_errors += len(errors)

                summary = f"{target}: +{len(installed)} installed, {len(skipped)} skipped, {len(errors)} error(s)"
                summaries.append(summary)
                self.obs_workflow_log(f"Overlay Install: {summary}")

                if hasattr(app.obs_workflow_state, "add_event"):
                    app.obs_workflow_state.add_event(f"Overlay Install: {summary}")

            except Exception as e:
                total_errors += 1
                summaries.append(f"{target}: ERROR {e}")
                self.obs_workflow_log(f"Overlay Install ERROR [{target}]: {e}")

        self.obs_workflow_mark_command(
            f"Overlay Install: {successes}/{len(targets)} scene(s), {total_installed} source(s), {total_errors} error(s)"
        )

        # Rescan to update dashboard.
        try:
            self.obs_workflow_scan_overlay_health(silent=True)
        except Exception as e:
            self.obs_workflow_log(f"Overlay Health rescan after install failed: {e}")

        details = "\n".join(summaries[:12])
        if len(summaries) > 12:
            details += f"\n... and {len(summaries) - 12} more"

        messagebox.showinfo(
            "Overlay Installer",
            f"Install abgeschlossen.\n\nSzenen: {successes}/{len(targets)}\nQuellen installiert: {total_installed}\nFehler: {total_errors}\n\n{details}"
        )

        app.show_obs_workflow_page()



