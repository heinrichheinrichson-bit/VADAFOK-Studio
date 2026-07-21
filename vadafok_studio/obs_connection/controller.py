"""Connection, health check and source diagnostics for OBS."""

from __future__ import annotations

import time
from tkinter import messagebox


class OBSConnectionController:
    def __init__(self, app):
        self.app = app

    def show_page(self):
        from .page import show_obs_connection_page

        result = show_obs_connection_page(self.app, self)
        self.refresh_status(probe=False)
        return result

    def validate_endpoint(self, show_message=True):
        host = str(self.app.host.get() or "").strip()
        port_text = str(self.app.port.get() or "").strip()
        error = ""
        if not host:
            error = "Bitte einen OBS-Host eintragen."
        else:
            try:
                port = int(port_text)
                if not 1 <= port <= 65535:
                    raise ValueError
            except (TypeError, ValueError):
                error = "Der Port muss zwischen 1 und 65535 liegen."
        if error and show_message:
            messagebox.showwarning("OBS Connection", error)
        return not error

    def connect(self, show_dialog=True):
        app = self.app
        if not self.validate_endpoint(show_message=show_dialog):
            self._set_status("● Eingaben prüfen", "#D86A6A")
            return False
        started = time.perf_counter()
        self._set_status("● Verbindung wird hergestellt …", "#E0B86A")
        try:
            app.obs.connect(
                app.host.get().strip(), app.port.get().strip(), app.password.get(),
            )
            elapsed_ms = round((time.perf_counter() - started) * 1000)
            self._sync_shared_status(True)
            app.save_config()
            version = app.obs.version_summary()
            detail = f" · {version}" if version else ""
            self._set_status(f"● Verbunden · {elapsed_ms} ms{detail}", "#6EE08C")
            self._set_detail("Verbindung erfolgreich. Die Quellen können jetzt geprüft werden.")
            if show_dialog:
                messagebox.showinfo("OBS", "Verbindung erfolgreich.")
            return True
        except Exception as error:
            self._sync_shared_status(False)
            self._set_status("● Nicht verbunden", "#D86A6A")
            self._set_detail(self.friendly_error(error))
            if show_dialog:
                messagebox.showerror("OBS Verbindung fehlgeschlagen", self.friendly_error(error))
            return False

    def disconnect(self):
        self.app.obs.disconnect()
        self._sync_shared_status(False)
        self._set_status("● Getrennt", "#BCA870")
        self._set_detail("Die Verbindung zu OBS wurde geschlossen.")
        return True

    def refresh_status(self, probe=True):
        connected = bool(self.app.obs.connected)
        if probe and connected:
            connected = self.app.obs.probe()
        self._sync_shared_status(connected)
        if connected:
            version = self.app.obs.version_summary()
            self._set_status(
                "● Verbunden" + (f" · {version}" if version else ""), "#6EE08C",
            )
            self._set_detail("OBS WebSocket antwortet.")
        else:
            self._set_status("● Nicht verbunden", "#D86A6A")
            self._set_detail("Mit ‘VERBINDEN’ wird OBS WebSocket geprüft.")
        return connected

    def test_connection(self):
        if not self.refresh_status(probe=True):
            return self.connect(show_dialog=False)
        return True

    def diagnose_sources(self):
        app = self.app
        self._clear_diagnostics()
        if not self.refresh_status(probe=True):
            self._add_diagnostic("Verbindung", "FEHLT", "#D86A6A")
            self._set_detail("Zuerst mit OBS verbinden, danach die Quellen prüfen.")
            return False
        try:
            configured_scene = app.scene_name.get().strip()
            scene = configured_scene or app.obs.get_current_scene_name()
            scenes = app.obs.get_scene_list()
            if not scene:
                raise RuntimeError("OBS meldet keine aktive Szene.")
            if configured_scene and configured_scene not in scenes:
                self._add_diagnostic(f"Szene: {configured_scene}", "NICHT GEFUNDEN", "#D86A6A")
                self._set_detail("Die konfigurierte Szene existiert in OBS nicht.")
                return False

            self._add_diagnostic(f"Szene: {scene}", "OK", "#8FE6A0")
            source_names = {
                str(item.get("name", "")).strip()
                for item in app.obs.get_scene_sources_recursive(scene)
            }
            smart_png = app.caption_engine.get() == "smart_png"
            checks = [
                ("Caption Group", app.caption_group.get(), True),
                ("Text Source", app.caption_text.get(), not smart_png),
                ("Banner Source", app.caption_banner_source.get(), not smart_png),
                ("Render Source", app.caption_render_source.get(), smart_png),
                ("Scene Card Source", app.scene_card_source.get(), False),
                (
                    "Stream Effect Source", app.stream_effect_source.get(),
                    bool(app.config_data.get("stream_effect_enabled", False)),
                ),
            ]
            missing = 0
            optional_missing = 0
            for label, raw_name, required in checks:
                name = str(raw_name or "").strip()
                if not name:
                    result = "NICHT KONFIGURIERT" if required else "OPTIONAL"
                    self._add_diagnostic(label, result, "#D86A6A" if required else "#BCA870")
                    missing += int(required)
                    optional_missing += int(not required)
                elif name in source_names:
                    self._add_diagnostic(f"{label}: {name}", "OK", "#8FE6A0")
                else:
                    result = "FEHLT" if required else "OPTIONAL FEHLT"
                    self._add_diagnostic(
                        f"{label}: {name}", result,
                        "#D86A6A" if required else "#E0B86A",
                    )
                    missing += int(required)
                    optional_missing += int(not required)
            if missing:
                self._set_detail(f"{missing} benötigte Zuordnung(en) fehlen.")
                return False
            if optional_missing:
                self._set_detail(
                    "Alle benötigten Quellen sind bereit · "
                    f"{optional_missing} optionale Zuordnung(en) fehlen.",
                )
                return True
            self._set_detail("Alle konfigurierten VADAFOK-Quellen wurden gefunden.")
            return True
        except Exception as error:
            self._add_diagnostic("Quellenprüfung", "FEHLER", "#D86A6A")
            self._set_detail(self.friendly_error(error))
            return False

    @staticmethod
    def friendly_error(error):
        text = str(error or "Unbekannter Fehler").strip()
        lower = text.casefold()
        if "auth" in lower or "password" in lower:
            return "Authentifizierung fehlgeschlagen. Bitte das OBS-WebSocket-Passwort prüfen."
        if "refused" in lower or "10061" in lower:
            return "OBS ist unter diesem Host und Port nicht erreichbar. Ist WebSocket aktiviert?"
        if "timed out" in lower or "timeout" in lower:
            return "OBS antwortet nicht. Bitte Host, Port und Firewall prüfen."
        return text

    def toggle_password(self):
        entry = getattr(self.app, "obs_password_entry", None)
        if entry is None:
            return
        visible = entry.cget("show") == ""
        entry.configure(show="*" if visible else "")
        button = getattr(self.app, "obs_password_toggle", None)
        if button is not None:
            button.configure(text="ANZEIGEN" if visible else "VERBERGEN")

    def _sync_shared_status(self, connected):
        app = self.app
        try:
            app.obs_workflow_set_sidebar_status(bool(connected))
        except Exception:
            label = getattr(app, "status_label", None)
            if label is not None:
                label.configure(
                    text="● Connected" if connected else "● Not connected",
                    text_color="#6EE08C" if connected else "#D86A6A",
                )

    def _set_status(self, text, color):
        label = getattr(self.app, "obs_connection_status_label", None)
        if label is not None:
            label.configure(text=text, text_color=color)

    def _set_detail(self, text):
        label = getattr(self.app, "obs_connection_detail_label", None)
        if label is not None:
            label.configure(text=text)

    def _clear_diagnostics(self):
        frame = getattr(self.app, "obs_diagnostics_list", None)
        if frame is None:
            return
        for child in frame.winfo_children():
            child.destroy()

    def _add_diagnostic(self, label, result, color):
        frame = getattr(self.app, "obs_diagnostics_list", None)
        if frame is None:
            return
        import customtkinter as ctk

        row = ctk.CTkFrame(frame, fg_color="#191919", corner_radius=8)
        row.pack(fill="x", pady=3)
        ctk.CTkLabel(row, text=label, anchor="w", text_color="#E8DFC5").pack(
            side="left", fill="x", expand=True, padx=10, pady=7,
        )
        ctk.CTkLabel(row, text=result, text_color=color).pack(side="right", padx=10)
