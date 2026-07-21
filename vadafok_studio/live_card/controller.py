"""Live Card and Quick Caption behavior controller.

The application continues to own Tk variables, widgets, OBS services, and
runtime state. This controller moves the existing Live Card orchestration
without changing the F8 or voice-command behavior.
"""

from __future__ import annotations

from pathlib import Path
from tkinter import filedialog, messagebox

import customtkinter as ctk

from ..core.config import load_asset_meta, save_config
from ..logging_setup import LOGGER
from ..services.sound_service import SoundService
from ..services.sound_effect_selection import effect_display_name, portable_effect_path

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"
DARK = "#090909"
PANEL = "#111111"
TEXT = "#F2E2B6"


class LiveCardController:
    """Coordinate Live Card UI, sound selection, and Quick Caption opening."""

    def __init__(self, app):
        self.app = app

    def open_live_card_banner_picker(self, slot=None):
        """Open Library directly in Banners for changing the Live Card banner."""
        app = self.app
        app.library_banner_picker_mode = True
        app.library_banner_target_slot = slot
        app.library_return_page = "Live Card"
        app.show_library()
        app.open_library_section("Banners")

    def return_to_live_card_from_library(self):
        app = self.app
        # Re-read the Library metadata before rebuilding the four Live Card
        # favorite slots. This keeps CHANGE / MANAGE reliable even when the
        # favorites file was changed while the picker was open.
        app.asset_meta = load_asset_meta()
        app.library_banner_picker_mode = False
        app.library_banner_target_slot = None
        app.library_return_page = None
        self.show_live_card()

    def show_live_card_page(self):
        """Compatibility alias used by Silent Director."""
        app = self.app
        return self.show_live_card()

    def live_card_current_banner_name(self):
        app = self.app
        path = str(app.config_data.get("selected_banner_path", "") or "").strip()
        if not path:
            return "Kein Banner ausgewählt"
        try:
            return Path(path).name
        except Exception:
            return path

    def live_card_current_effect_name(self):
        app = self.app
        return effect_display_name(app.config_data.get("selected_sound_effect", ""))

    def _sync_sound_service_project(self):
        """Keep the SoundService aligned with the currently selected project."""
        app = self.app
        project = str(app.project_folder.get() or "").strip()
        if getattr(app, "sound_service", None) is None:
            app.sound_service = SoundService(project)
        elif str(app.sound_service.project_dir or "") != str(Path(project).expanduser().resolve(strict=False) if project else ""):
            app.sound_service.set_project_dir(project or None)
        return app.sound_service

    def default_sound_favorites(self):
        app = self.app
        return [
            {"name": "Favorit 1", "file": ""},
            {"name": "Favorit 2", "file": ""},
            {"name": "Favorit 3", "file": ""},
            {"name": "Favorit 4", "file": ""},
        ]

    def _ensure_sound_favorites(self):
        """Normalize the four quick-select sound slots in config."""
        app = self.app
        raw = app.config_data.get("sound_favorites", [])
        normalized = []
        for index in range(4):
            fallback = self.default_sound_favorites()[index]
            item = raw[index] if isinstance(raw, list) and index < len(raw) else {}
            if not isinstance(item, dict):
                item = {}
            normalized.append({
                "name": str(item.get("name", fallback["name"]) or fallback["name"]).strip(),
                "file": str(item.get("file", "") or "").strip(),
            })
        app.config_data["sound_favorites"] = normalized
        return normalized

    def _apply_selected_sound_effect(self, relative):
        """Persist one portable sound path and align the OBS media source."""
        app = self.app
        relative = str(relative or "").strip()
        if not relative:
            return False
        service = self._sync_sound_service_project()
        if not service.exists(relative):
            messagebox.showerror(
                "Stream Effect",
                "Die ausgewählte WAV-Datei wurde im Projektordner Sounds nicht gefunden.",
            )
            return False

        app.config_data["selected_sound_effect"] = relative
        save_config(app.config_data)

        try:
            if app.obs.probe():
                media_file = service.resolve(relative)
                source_name = app.stream_effect_source.get().strip()
                if media_file is not None and source_name:
                    app.obs.set_media_file(source_name, media_file)
        except Exception:
            LOGGER.exception("OBS Stream Effect source could not be updated for %s", relative)

        label = getattr(app, "live_card_effect_name_label", None)
        if label is not None:
            try:
                label.configure(text=self.live_card_current_effect_name())
            except Exception:
                pass
        self.refresh_sound_favorite_buttons()
        return True

    def select_sound_favorite(self, index):
        app = self.app
        favorites = self._ensure_sound_favorites()
        if index < 0 or index >= len(favorites):
            return False
        favorite = favorites[index]
        relative = str(favorite.get("file", "") or "").strip()
        if not relative:
            messagebox.showinfo(
                "Sound-Favorit",
                "Dieser Favorit ist noch nicht eingerichtet.",
            )
            return False
        return self._apply_selected_sound_effect(relative)

    def refresh_sound_favorite_buttons(self):
        app = self.app
        favorites = self._ensure_sound_favorites()
        selected = str(app.config_data.get("selected_sound_effect", "") or "").strip()
        for index, button in enumerate(getattr(app, "sound_favorite_buttons", [])):
            if index >= len(favorites):
                continue
            favorite = favorites[index]
            name = str(favorite.get("name", "") or f"Favorit {index + 1}")
            configured = bool(str(favorite.get("file", "") or "").strip())
            active = configured and str(favorite.get("file", "")).strip() == selected
            button.configure(
                text=name,
                fg_color=GOLD if active else ("#333333" if configured else "#1C1C1C"),
                text_color="#111111" if active else TEXT,
                hover_color=GOLD_DARK if active else "#444444",
            )

    def open_sound_favorites_editor(self):
        app = self.app
        from ..sound_favorites.editor import open_sound_favorites_editor_window
        return open_sound_favorites_editor_window(app)

    def change_live_card_effect(self):
        """Choose one portable WAV path below <Project>/Sounds."""
        app = self.app
        project = str(app.project_folder.get() or "").strip()
        if not project:
            messagebox.showwarning(
                "Stream Effect",
                "Bitte zuerst unter Settings einen Projektordner auswählen.",
            )
            return False

        service = self._sync_sound_service_project()
        sounds_dir = service.sounds_dir
        if sounds_dir is None or not sounds_dir.is_dir():
            messagebox.showwarning(
                "Stream Effect",
                f"Der Sound-Ordner wurde nicht gefunden:\n\n{Path(project) / 'Sounds'}",
            )
            return False

        selected = filedialog.askopenfilename(
            title="Stream Effect auswählen",
            initialdir=str(sounds_dir),
            filetypes=[("WAV Audio", "*.wav"), ("Alle Dateien", "*.*")],
        )
        if not selected:
            return False

        relative = portable_effect_path(service, selected)
        if relative is None:
            messagebox.showerror(
                "Stream Effect",
                "Bitte eine vorhandene WAV-Datei innerhalb des Projektordners Sounds auswählen.",
            )
            return False

        return self._apply_selected_sound_effect(relative)

    def set_stream_effect_enabled(self):
        """Persist whether SHOW should automatically play the selected effect."""
        app = self.app
        enabled = bool(app.stream_effect_enabled.get())
        app.config_data["stream_effect_enabled"] = enabled
        save_config(app.config_data)
        return enabled

    def preview_live_card_effect(self):
        """Preview the configured effect independently of automatic SHOW playback."""
        app = self.app
        relative = str(app.config_data.get("selected_sound_effect", "") or "").strip()
        if not relative:
            messagebox.showwarning(
                "Stream Effect",
                "Bitte zuerst einen Effekt auswählen.",
            )
            return False

        service = self._sync_sound_service_project()
        if not service.exists(relative):
            messagebox.showerror(
                "Stream Effect",
                "Die ausgewählte WAV-Datei wurde im Projektordner Sounds nicht gefunden.",
            )
            return False
        if not service.play(relative):
            messagebox.showerror(
                "Stream Effect",
                "Der Sound konnte nicht abgespielt werden. WAV-Wiedergabe wird derzeit unter Windows unterstützt.",
            )
            return False
        return True

    def reset_live_card_text(self):
        """Reset only the Live Card editor text and refresh the preview."""
        app = self.app
        if not hasattr(app, "message_box"):
            return
        app.message_box.delete("1.0", "end")
        app.message_box.insert("1.0", "CHAT WAS RIGHT.")
        app.live_card_pending_text = ""
        try:
            from .voice_control.live_card_voice import reset_live_card_translation
            reset_live_card_translation(app)
        except Exception:
            pass
        app.schedule_live_card_preview()
        try:
            app.message_box.focus_set()
        except Exception:
            pass

    def show_live_card(self):
        app = self.app
        app.set_active("Live Card")
        app.clear_main()
        app.page_title("Live Card")
        content = ctk.CTkFrame(app.main, fg_color=DARK)
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(content, fg_color=PANEL, corner_radius=18)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(left, text="Message", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")
        app.message_box = ctk.CTkTextbox(left, height=180, font=ctk.CTkFont(size=18), fg_color="#050505", border_color=GOLD_DARK, border_width=1)
        app.message_box.grid(row=1, column=0, padx=18, pady=(0, 12), sticky="nsew")
        app.message_box.insert("1.0", app.live_card_pending_text or "CHAT WAS RIGHT.")
        app.message_box.bind("<Return>", app.enter_to_show)
        app.message_box.bind("<KeyRelease>", lambda _event: app.schedule_live_card_preview())

        if not hasattr(app, "live_card_translation_var"):
            app.live_card_translation_var = ctk.StringVar(
                value="Speak to prepare an English translation."
            )
        translation_box = ctk.CTkFrame(left, fg_color="#0B0B0B", corner_radius=10)
        translation_box.grid(row=2, column=0, sticky="ew", padx=18, pady=(0, 8))
        translation_box.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            translation_box,
            text="ENGLISH PREVIEW · VADAFOK ENGLISH TO USE",
            text_color="#BCA870",
            font=ctk.CTkFont(size=12, weight="bold"),
        ).grid(row=0, column=0, padx=12, pady=(9, 2), sticky="w")
        ctk.CTkLabel(
            translation_box,
            textvariable=app.live_card_translation_var,
            text_color=TEXT,
            justify="left",
            anchor="w",
            wraplength=650,
        ).grid(row=1, column=0, padx=12, pady=(2, 10), sticky="ew")

        row = ctk.CTkFrame(left, fg_color="transparent")
        row.grid(row=3, column=0, sticky="ew", padx=18, pady=8)
        row.grid_columnconfigure((0, 1), weight=1)
        app.option(
            row,
            "Engine",
            ["obs_text", "smart_png"],
            app.caption_engine,
            0
        )
        app.option(
            row,
            "Duration",
            ["3", "5", "7", "10", "15"],
            app.duration,
            1
        )

        btns = ctk.CTkFrame(left, fg_color="transparent")
        btns.grid(row=4, column=0, sticky="ew", padx=18, pady=(14, 18))
        btns.grid_columnconfigure((0, 1, 2, 3), weight=1)
        ctk.CTkButton(btns, text="SHOW", height=46, fg_color=GOLD, hover_color=GOLD_DARK, text_color="#111111", command=app.show_card).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(btns, text="HIDE", height=46, fg_color="#333333", command=app.hide_card).grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkButton(btns, text="CLEAR", height=46, fg_color="#222222", command=app.clear_text).grid(row=0, column=2, padx=5, sticky="ew")
        ctk.CTkButton(btns, text="SAVE QUICK", height=46, fg_color="#222222", command=app.save_current_quick).grid(row=0, column=3, padx=5, sticky="ew")

        quick_save_box = ctk.CTkFrame(left, fg_color="#0B0B0B", corner_radius=10)
        quick_save_box.grid(row=5, column=0, sticky="ew", padx=18, pady=(0, 12))
        quick_save_box.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(quick_save_box, text="Quick Save Category", text_color="#BCA870").grid(row=0, column=0, padx=(10, 8), pady=10, sticky="w")
        cats = app.quick_cards_categories()
        if app.quick_cards_target_category.get() not in cats:
            app.quick_cards_target_category.set("Chat" if "Chat" in cats else cats[0])
        ctk.CTkOptionMenu(
            quick_save_box,
            values=cats,
            variable=app.quick_cards_target_category,
            fg_color="#333333",
            button_color="#444444",
            button_hover_color="#555555"
        ).grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew")

        right = ctk.CTkFrame(content, fg_color=PANEL, corner_radius=18)
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(right, text="Live Preview", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")
        app.preview_frame = ctk.CTkFrame(right, fg_color="#020202", corner_radius=14, border_width=1, border_color="#3A2A0D")
        app.preview_frame.grid(row=1, column=0, padx=18, pady=(0, 8), sticky="nsew")

        def preview_frame_resized(event):
            size = (event.width, event.height)
            if min(size) < 160 or size == getattr(app, "live_preview_frame_size", None):
                return
            app.live_preview_frame_size = size
            app.schedule_live_card_preview()

        app.preview_frame.bind("<Configure>", preview_frame_resized, add="+")

        app.render_status_label = ctk.CTkLabel(
            right,
            text="Preview wartet...",
            text_color="#BCA870",
            justify="left",
            anchor="w"
        )
        app.render_status_label.grid(
            row=2,
            column=0,
            padx=18,
            pady=(0, 4),
            sticky="ew"
        )

        banner_info = ctk.CTkFrame(
            right,
            fg_color="#0B0B0B",
            corner_radius=10,
            border_color="#2D2818",
            border_width=1
        )
        banner_info.grid(
            row=3,
            column=0,
            padx=18,
            pady=(0, 8),
            sticky="ew"
        )
        banner_info.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            banner_info,
            text="CURRENT BANNER",
            text_color="#777777",
            font=ctk.CTkFont(size=10, weight="bold"),
            anchor="w"
        ).grid(
            row=0,
            column=0,
            padx=12,
            pady=(8, 1),
            sticky="ew"
        )

        app.live_card_banner_name_label = ctk.CTkLabel(
            banner_info,
            text=self.live_card_current_banner_name(),
            text_color=GOLD,
            wraplength=330,
            justify="left",
            anchor="w",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        app.live_card_banner_name_label.grid(
            row=1,
            column=0,
            padx=12,
            pady=(0, 8),
            sticky="ew"
        )

        preview_actions = ctk.CTkFrame(
            right,
            fg_color="transparent"
        )
        preview_actions.grid(
            row=4,
            column=0,
            padx=18,
            pady=(0, 8),
            sticky="ew"
        )
        preview_actions.grid_columnconfigure((0, 1), weight=1)

        ctk.CTkButton(
            preview_actions,
            text="REFRESH PREVIEW",
            height=38,
            fg_color="#333333",
            hover_color="#444444",
            command=app.update_render_preview
        ).grid(
            row=0,
            column=0,
            padx=(0, 4),
            sticky="ew"
        )

        ctk.CTkButton(
            preview_actions,
            text="RESET TEXT",
            height=38,
            fg_color="#333333",
            hover_color="#444444",
            command=app.reset_live_card_text
        ).grid(
            row=0,
            column=1,
            padx=(4, 0),
            sticky="ew"
        )

        ctk.CTkButton(
            right,
            text="CHANGE BANNER",
            height=42,
            fg_color=GOLD,
            text_color="#111111",
            hover_color=GOLD_DARK,
            command=app.open_live_card_banner_picker
        ).grid(
            row=5,
            column=0,
            padx=18,
            pady=(0, 10),
            sticky="ew"
        )

        effect_info = ctk.CTkFrame(
            right,
            fg_color="#0B0B0B",
            corner_radius=10,
            border_color="#2D2818",
            border_width=1,
        )
        effect_info.grid(
            row=6,
            column=0,
            padx=18,
            pady=(0, 8),
            sticky="ew",
        )
        effect_info.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            effect_info,
            text="STREAM EFFECT",
            text_color="#777777",
            font=ctk.CTkFont(size=10, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, padx=12, pady=(8, 1), sticky="ew")
        app.live_card_effect_name_label = ctk.CTkLabel(
            effect_info,
            text=self.live_card_current_effect_name(),
            text_color=GOLD,
            wraplength=330,
            justify="left",
            anchor="w",
            font=ctk.CTkFont(size=12, weight="bold"),
        )
        app.live_card_effect_name_label.grid(
            row=1, column=0, padx=12, pady=(0, 5), sticky="ew"
        )
        ctk.CTkCheckBox(
            effect_info,
            text="Sound automatisch bei SHOW abspielen",
            variable=app.stream_effect_enabled,
            command=app.set_stream_effect_enabled,
            text_color=TEXT,
            fg_color=GOLD,
            hover_color=GOLD_DARK,
            border_color="#777777",
            checkmark_color="#111111",
        ).grid(row=2, column=0, padx=12, pady=(0, 10), sticky="w")

        favorites_box = ctk.CTkFrame(
            right,
            fg_color="#0B0B0B",
            corner_radius=10,
            border_color="#2D2818",
            border_width=1,
        )
        favorites_box.grid(row=7, column=0, padx=18, pady=(0, 8), sticky="ew")
        favorites_box.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkLabel(
            favorites_box,
            text="★ SOUND-FAVORITEN",
            text_color="#777777",
            font=ctk.CTkFont(size=10, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, columnspan=2, padx=12, pady=(8, 5), sticky="ew")
        app.sound_favorite_buttons = []
        for index in range(4):
            button = ctk.CTkButton(
                favorites_box,
                text=f"Favorit {index + 1}",
                height=32,
                fg_color="#1C1C1C",
                hover_color="#444444",
                command=lambda slot=index: self.select_sound_favorite(slot),
            )
            button.grid(
                row=1 + index // 2,
                column=index % 2,
                padx=(8 if index % 2 == 0 else 4, 4 if index % 2 == 0 else 8),
                pady=4,
                sticky="ew",
            )
            app.sound_favorite_buttons.append(button)
        ctk.CTkButton(
            favorites_box,
            text="FAVORITEN BEARBEITEN",
            height=30,
            fg_color="transparent",
            border_width=1,
            border_color="#555555",
            hover_color="#252525",
            command=app.open_sound_favorites_editor,
        ).grid(row=3, column=0, columnspan=2, padx=8, pady=(4, 8), sticky="ew")
        self.refresh_sound_favorite_buttons()

        effect_actions = ctk.CTkFrame(right, fg_color="transparent")
        effect_actions.grid(
            row=8, column=0, padx=18, pady=(0, 18), sticky="ew"
        )
        effect_actions.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(
            effect_actions,
            text="CHANGE EFFECT",
            height=38,
            fg_color=GOLD,
            text_color="#111111",
            hover_color=GOLD_DARK,
            command=app.change_live_card_effect,
        ).grid(row=0, column=0, padx=(0, 4), sticky="ew")
        ctk.CTkButton(
            effect_actions,
            text="PREVIEW",
            height=38,
            fg_color="#333333",
            hover_color="#444444",
            command=app.preview_live_card_effect,
        ).grid(row=0, column=1, padx=(4, 0), sticky="ew")

        app.schedule_live_card_preview()

    def live_card_set_message_text(self, text):
        app = self.app
        text = str(text or "").strip()
        if not text:
            return
        app.live_card_pending_text = text

        for attr in ("message_box", "message", "live_message", "live_card_message"):
            widget = getattr(app, attr, None)
            if widget is not None:
                try:
                    widget.delete("1.0", "end")
                    widget.insert("1.0", text)
                    return
                except Exception:
                    pass

    def live_card_get_message_text(self):
        app = self.app
        for attr in ("message_box", "message", "live_message", "live_card_message"):
            widget = getattr(app, attr, None)
            if widget is not None:
                try:
                    return widget.get("1.0", "end").strip()
                except Exception:
                    pass
        return str(getattr(app, "live_card_pending_text", "") or "").strip()

    def live_card_apply_pending_text(self):
        app = self.app
        text = str(getattr(app, "live_card_pending_text", "") or "").strip()
        if not text:
            return
        self.live_card_set_message_text(text)

    def open_quick_caption(self):
        """Open the compact F8 Quick Caption window."""
        app = self.app
        from vadafok_studio.quick_caption.window import open_quick_caption_window

        return open_quick_caption_window(app)
