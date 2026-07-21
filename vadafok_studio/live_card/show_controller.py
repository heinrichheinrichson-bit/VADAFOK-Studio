"""OBS SHOW orchestration for Live Cards."""

from __future__ import annotations

import threading
from typing import Any
from tkinter import messagebox

from ..core.sync_profiler import SyncProfiler
from ..logging_setup import LOGGER


class LiveCardShowController:
    """Send a prepared Live Card to OBS and schedule its removal."""

    def __init__(self, app: Any) -> None:
        self.app = app

    def play_selected_sound_effect_for_show(self, profiler=None):
        """Restart the configured OBS Media Source for SHOW, best-effort."""
        app = self.app
        if not bool(app.config_data.get("stream_effect_enabled", False)):
            if profiler is not None:
                profiler.mark("Sound skipped: automatic playback disabled")
            return None
        relative = str(
            app.config_data.get("selected_sound_effect", "") or ""
        ).strip()
        if not relative:
            if profiler is not None:
                profiler.mark("Sound skipped: no effect selected")
            return None
        source_name = app.stream_effect_source.get().strip()
        if not source_name:
            LOGGER.warning("No OBS Stream Effect Media Source is configured.")
            if profiler is not None:
                profiler.mark("Sound failed: no OBS Media Source configured")
            return False
        try:
            service = app._sync_sound_service_project()
            media_file = service.resolve(relative)
            if media_file is None or not service.exists(relative):
                LOGGER.warning("Configured Stream Effect is unavailable: %s", relative)
                if profiler is not None:
                    profiler.mark("Sound failed: WAV unavailable")
                return False
            if profiler is not None:
                profiler.mark("OBS media playback requested")
            app.obs.play_media_file(source_name, media_file)
            if profiler is not None:
                profiler.mark("OBS media playback request finished")
            return True
        except Exception:
            if profiler is not None:
                profiler.mark("OBS media playback request failed")
            LOGGER.exception(
                "OBS Stream Effect playback failed for %s via source %s",
                relative, source_name,
            )
            return False

    def show_card(self) -> None:
        app = self.app
        profiler = SyncProfiler(
            enabled=bool(app.config_data.get("sync_profiler_enabled", False)),
            session_name="LiveCard SHOW",
        )
        profiler.mark("SHOW event received")
        if not app.ensure_obs_ready():
            self._set_delivery_status("OBS nicht verbunden", "#D86A6A")
            profiler.mark("SHOW aborted: OBS not ready")
            profiler.save()
            return
        text = (
            app.message_box.get("1.0", "end").strip()
            if hasattr(app, "message_box") else ""
        ) or "..."
        shown = False
        try:
            scene = app.current_scene()
            profiler.mark("OBS scene resolved")
            if app.caption_engine.get() == "smart_png":
                if not self._show_smart_caption(scene, text, profiler):
                    return
            elif not self._show_obs_text_caption(scene, text, profiler):
                return

            profiler.mark("Banner group enable requested")
            app.obs.enable_source(scene, app.caption_group.get().strip(), True)
            profiler.mark("Banner group enable request finished")
            self._start_hide_timer(profiler)
            app.save_config()
            profiler.mark("Config save finished")
            sound_result = self.play_selected_sound_effect_for_show(profiler=profiler)
            seconds = max(1, int(app.duration.get()))
            self._set_delivery_status(
                f"● ON AIR · Auto-Hide in {seconds}s"
                + (" · Sound nicht verfügbar" if sound_result is False else ""),
                "#E0B86A" if sound_result is False else "#8FE6A0",
            )
            shown = True
            profiler.mark("SHOW completed")
        except Exception as error:
            profiler.mark(f"SHOW exception: {type(error).__name__}")
            self._set_delivery_status(f"SHOW-Fehler: {error}", "#D86A6A")
            messagebox.showerror("SHOW fehlgeschlagen", str(error))
        finally:
            profiler.save()

        if shown:
            try:
                app.obs_workflow_banner_action(
                    "SHOW Live Card", app.obs_workflow_current_live_text(),
                )
            except Exception:
                pass

    def hide_card(self) -> None:
        app = self.app
        self._cancel_hide_timer()
        if not app.ensure_obs_ready():
            self._set_delivery_status("OBS nicht verbunden", "#D86A6A")
            return
        try:
            app.obs.enable_source(
                app.current_scene(), app.caption_group.get().strip(), False,
            )
        except Exception:
            pass
        try:
            app.obs_workflow_banner_action("HIDE Live Card")
        except Exception:
            pass
        self._set_delivery_status("○ HIDDEN · bereit", "#BCA870")

    def cancel_pending_hide(self) -> None:
        """Cancel the background timer during shutdown or workflow changes."""
        self._cancel_hide_timer()

    def _show_smart_caption(self, scene, text: str, profiler) -> bool:
        app = self.app
        try:
            profiler.mark("Smart caption render requested")
            png = app.render_smart_caption(text, profiler=profiler)
            profiler.mark("Smart caption render finished")
            app.obs.set_image_file(app.caption_render_source.get().strip(), png)
            profiler.mark("OBS caption image update finished")
        except Exception:
            profiler.mark("SHOW failed: caption render source")
            self._set_delivery_status("SHOW-Fehler · Render Source", "#D86A6A")
            messagebox.showerror(
                "Caption Render Source nicht gefunden",
                f"Die OBS-Bildquelle '{app.caption_render_source.get().strip()}' "
                "wurde nicht gefunden.\n\nBitte OBS Connection prüfen.",
            )
            return False
        self._set_source_visibility(scene, app.caption_text.get().strip(), False)
        self._set_source_visibility(scene, app.caption_render_source.get().strip(), True)
        return True

    def _show_obs_text_caption(self, scene, text: str, profiler) -> bool:
        app = self.app
        banner_path = app.config_data.get("selected_banner_path", "")
        if banner_path:
            try:
                app.obs.set_image_file(
                    app.caption_banner_source.get().strip(), banner_path,
                )
                profiler.mark("OBS banner image update finished")
            except Exception:
                profiler.mark("SHOW failed: caption banner source")
                self._set_delivery_status("SHOW-Fehler · Banner Source", "#D86A6A")
                messagebox.showerror(
                    "Caption Banner Source nicht gefunden",
                    f"Die OBS-Bildquelle '{app.caption_banner_source.get().strip()}' "
                    "wurde nicht gefunden.\n\nBitte OBS Connection prüfen.",
                )
                return False
        try:
            app.obs.set_text(app.caption_text.get().strip(), text)
            profiler.mark("OBS caption text update finished")
        except Exception:
            profiler.mark("SHOW failed: text source")
            self._set_delivery_status("SHOW-Fehler · Text Source", "#D86A6A")
            messagebox.showerror(
                "Text Source nicht gefunden",
                f"Die OBS-Textquelle '{app.caption_text.get().strip()}' wurde "
                "nicht gefunden.\n\nBitte OBS Connection prüfen.",
            )
            return False
        self._set_source_visibility(scene, app.caption_render_source.get().strip(), False)
        self._set_source_visibility(scene, app.caption_text.get().strip(), True)
        return True

    def _set_source_visibility(self, scene, source: str, visible: bool) -> None:
        try:
            self.app.obs.enable_source(scene, source, visible)
        except Exception:
            pass

    def _start_hide_timer(self, profiler) -> None:
        app = self.app
        self._cancel_hide_timer()
        seconds = max(1, int(app.duration.get()))
        app.hide_timer = threading.Timer(
            seconds, lambda: app.after(0, self._auto_hide),
        )
        app.hide_timer.daemon = True
        app.hide_timer.start()
        profiler.mark("Hide timer started")

    def _auto_hide(self) -> None:
        self.app.hide_timer = None
        self.hide_card()

    def _cancel_hide_timer(self) -> None:
        timer = getattr(self.app, "hide_timer", None)
        if timer is not None:
            try:
                timer.cancel()
            except Exception:
                pass
        self.app.hide_timer = None

    def _set_delivery_status(self, text: str, color: str) -> None:
        label = getattr(self.app, "live_delivery_status_label", None)
        if label is not None:
            try:
                label.configure(text=text, text_color=color)
            except Exception:
                pass
