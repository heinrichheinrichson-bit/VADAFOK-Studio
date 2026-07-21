import time

import os
import sys
import subprocess
import tkinter as tk
from pathlib import Path
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image

from .core.config import TEMPLATE_PROFILES_PATH, load_config, save_config, load_favorites, save_favorites, load_asset_meta, save_asset_meta, EXPORT_DIR, load_json, save_json, CARD_VALUES_PATH
from .core.library import scan_library, scan_library_section, library_section_exists, ROOT_FOLDERS, guessed_tags
from .core.obs_controller import OBSController
from .core.caption_renderer import render_caption_png
from .core.template_store import list_templates, load_template, save_template, create_template, set_background_from_file, background_path, import_legacy_templates, delete_template, duplicate_template, rename_template, set_default_template, get_default_template, ensure_background_file, template_dir
from .core.recent_templates import load_recent_templates, record_recent_template, remove_recent_template
from .card_creator import (
    CardBatchController,
    CardCreatorController,
    CardCreatorState,
    CardExportController,
    CardPreviewController,
    CardDataController,
    CardStyleController,
    CardRenderService,
)
from .card_creator.page import (
    build_batch_panel,
    show_card_creator_page as build_card_creator_page,
)
from .card_creator.form_view import build_card_form
from .card_creator.template_list_view import (
    build_all_template_buttons,
    refresh_all_templates,
    refresh_recent_templates,
)
from .template_editor import (
    TemplateEditorController,
    TemplateRefreshManager,
    build_layers_panel,
    build_properties_panel,
    draw_canvas,
    update_fields_overlay,
)
from .template_editor import smart_guides
from .template_editor import mouse_controller
from .template_editor import selection_controller
from .template_editor import layer_controller
from .library import LibraryController
from .library.page import show_library_page
from .library.grid_view import render_asset_grid, render_folder_overview
from .library.preview_view import make_thumbnail_label, select_library_item
from .library import asset_actions as library_asset_actions
from .library import use_actions as library_use_actions
from .banner_editor.controller import BannerEditorController
from .obs_workflow.controller import OBSWorkflowController
from .settings.controller import SettingsController
from .live_card.controller import LiveCardController
from .silent_director import render_actions_list
from .silent_director import render_filtered_presets
from .silent_director import run_preset as run_silent_director_preset
from .silent_director import show_silent_director_page as build_silent_director_page
from .silent_director.drag_controller import (
    drag_cancel as cancel_silent_director_drag,
    drag_motion as move_silent_director_drag,
    drag_release as release_silent_director_drag,
    drag_start as start_silent_director_drag,
    drag_target_from_y as silent_director_drag_target,
    hide_floating_drop_indicator as hide_silent_director_drop_indicator,
    show_floating_drop_indicator as show_silent_director_drop_indicator,
)
from .silent_director import management_controller as director_management
from .silent_director import support_controller as director_support
from .core.image_view import load_rgba, fit_image_to_box, pil_to_tk_photo_data, image_status
from .core.layout_engine import banner_profile_to_layout_field, apply_layout_field_to_banner_profile, create_default_template, render_template_card, render_template_card_image
from .core import style_engine
from .core import export_engine
from .core import batch_engine
from .core import text_library_engine
from .core import obs_workflow
from .core import scene_favorites
from .core import silent_director
from .core.banner_profiles import load_banner_profiles, save_banner_profiles, ensure_profile, has_profile, profile_count, reset_profile_style
from .version import APP_TITLE, APP_USER_MODEL_ID, SIDEBAR_VERSION
from .logging_setup import LOGGER
from .services.sound_service import SoundService
from .services.sound_effect_selection import effect_display_name, portable_effect_path
from .core.sync_profiler import SyncProfiler
LOGGER.info("app.py loaded successfully")

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"
DARK = "#090909"
PANEL = "#111111"
TEXT = "#F2E2B6"

class VadafokStudio(ctk.CTk):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        self.wm_title(APP_TITLE)
        self.geometry("1360x840")
        self.minsize(1160, 740)

        self._vadafok_icon_photo = None
        try:
            if sys.platform == "win32":
                import ctypes
                ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_USER_MODEL_ID)

            icon_dir = Path(__file__).resolve().parent / "assets" / "icons"
            ico_file = icon_dir / "vadafok_icon.ico"
            png_file = icon_dir / "vadafok_icon.png"

            if ico_file.exists():
                self.iconbitmap(str(ico_file))

            if png_file.exists():
                self._vadafok_icon_photo = tk.PhotoImage(file=str(png_file))
                self.iconphoto(True, self._vadafok_icon_photo)
        except Exception:
            LOGGER.warning("Unable to configure application icon", exc_info=True)

        self.config_data = load_config()
        self.settings_controller = SettingsController(self)
        self.favorites = load_favorites()
        self.asset_meta = load_asset_meta()
        self.banner_profiles = load_banner_profiles()
        self.template_profiles = load_json(TEMPLATE_PROFILES_PATH, {})
        self.template_store_migrated = import_legacy_templates(self.template_profiles)
        self.template_selected_name = "Default Stream Plan"
        self.template_editor_controller = TemplateEditorController(self, list_templates, load_template)
        self.template_refresh_manager = TemplateRefreshManager(self)
        self.template_selected_field = None
        self.template_selected_fields = set()
        self.template_shift_down = False
        self.template_ctrl_down = False
        self.template_drag_mode = None
        self.template_drag_start = None
        self.template_drag_original = None
        self.template_group_drag_originals = None
        self.template_undo_stack = []
        self.template_redo_stack = []
        self.template_history_limit = 80
        self.template_drag_history_snapshot = None
        self.template_rename_entry = None
        self.template_renaming_kind = None
        self.template_renaming_target = None
        self.template_marquee_active = False
        self.template_marquee_start = None
        self.template_marquee_item = None
        self.template_marquee_add_mode = False
        self.template_collapsed_groups = set()
        self.template_layer_drag_index = None
        self.template_layer_drag_start_y = None
        self.template_layer_drag_indicator = None
        self.template_layer_drop_indicator = None
        self.template_layer_drop_target = None
        self.template_working_data = None
        self.template_zoom_factor = 1.0
        self.template_zoom_label_var = ctk.StringVar(value="100%")
        self.template_pan_x = 0
        self.template_pan_y = 0
        self.template_pan_active = False
        self.template_pan_start = None
        self.template_pan_origin = None
        self.template_smart_guides_enabled = ctk.BooleanVar(value=True)
        self.template_smart_snap_enabled = ctk.BooleanVar(value=True)
        self.template_smart_guide_tolerance = 8
        self.template_hover_mode = None
        self.template_prop_name = ctk.StringVar(value="")
        self.template_prop_font_family = ctk.StringVar(value="")
        self.template_prop_font_size = ctk.IntVar(value=90)
        self.template_prop_text_color = ctk.StringVar(value="#FFFFFF")
        self.template_prop_stroke_color = ctk.StringVar(value="#000000")
        self.template_prop_stroke_width = ctk.IntVar(value=3)
        self.template_prop_uppercase = ctk.BooleanVar(value=True)
        self.card_selected_template = ctk.StringVar(value="")
        self.card_creator_state = CardCreatorState()
        self.card_creator_controller = CardCreatorController(
            self,
            list_templates,
            create_template,
            get_default_template,
            load_template,
            state=self.card_creator_state,
        )
        self.card_recent_templates = self.card_creator_controller.load_recent()
        self.card_creator_values = {}
        self.card_saved_values = load_json(CARD_VALUES_PATH, {})
        self.card_creator_preview_image = None
        self.card_creator_preview_label = None
        self.card_preview_update_job = None
        self.card_values_save_job = None
        self.card_output_name = ctk.StringVar(value="")
        self.card_auto_preview = ctk.BooleanVar(value=True)
        self.card_export_profile = ctk.StringVar(value="Broadcast PNG")
        self.card_export_controller = CardExportController(
            self,
            export_engine,
            EXPORT_DIR,
            os.startfile,
            state=self.card_creator_state,
        )
        self.card_preview_controller = CardPreviewController(
            self,
            export_engine,
            render_template_card_image,
            state=self.card_creator_state,
        )
        self.card_data_controller = CardDataController(
            self,
            self.card_creator_state,
            lambda values: save_json(CARD_VALUES_PATH, values),
        )
        self.card_style_controller = CardStyleController(
            self, style_engine, load_template, save_template
        )
        self.card_render_service = CardRenderService(
            self,
            load_template,
            background_path,
            template_dir,
            EXPORT_DIR,
            render_template_card,
            export_engine,
        )
        self.card_batch_controller = CardBatchController(
            self, self.card_creator_state, list_templates, batch_engine
        )
        self.obs = OBSController()
        self.obs_workflow_state = obs_workflow.OBSWorkflowState()
        self.obs_workflow_controller = OBSWorkflowController(self)
        self.scene_favorites = scene_favorites.load_favorites()
        self.silent_director_presets = silent_director.load_presets()
        self.silent_director_selected = ctk.StringVar(value=self.silent_director_presets[0]['name'] if self.silent_director_presets else '')
        self.silent_director_new_name = ctk.StringVar(value='')
        self.silent_director_search_var = ctk.StringVar(value='')
        self.silent_director_favorites_only = ctk.BooleanVar(value=False)
        self.silent_director_editor_icon = ctk.StringVar(value='AUTO')
        self.silent_director_preset_list_frame = None
        self.silent_director_editor_name = ctk.StringVar(value='')
        self.silent_director_editor_scene = ctk.StringVar(value='')
        self.silent_director_editor_show_banner = ctk.BooleanVar(value=False)
        self.silent_director_action_type = ctk.StringVar(value='switch_scene')
        self.silent_director_action_scene = ctk.StringVar(value='')
        self.silent_director_action_source = ctk.StringVar(value='')
        self.silent_director_action_text = ctk.StringVar(value='')
        self.silent_director_wait_seconds = ctk.StringVar(value="5")
        self.silent_director_edit_index = None
        self.silent_director_action_button_text = ctk.StringVar(value="+ ADD ACTION")
        self.silent_director_dynamic_frames = {}
        self.silent_director_drag_index = None
        self.silent_director_drop_index = None
        self.silent_director_action_rows = []
        self.silent_director_drag_active = False
        self.silent_director_drop_overlay = None
        self.silent_director_drop_overlay_label = None
        self.silent_director_dragged_card = None
        self.silent_director_drag_target = None
        self.director_status_var = ctk.StringVar(value="READY")
        self.director_current_action_var = ctk.StringVar(value="-")
        self.director_progress_var = ctk.StringVar(value="0 / 0")
        self.director_progress_percent_var = ctk.DoubleVar(value=0.0)
        self.director_stop_requested = False
        self.director_log_entries = []
        self.director_active_action_index = None
        self.director_action_card_widgets = {}
        self.director_log_text_var = ctk.StringVar(value="No Director run yet.")
        self.obs_workflow_current_scene_var = ctk.StringVar(value="Unknown")
        self.obs_workflow_last_switch_var = ctk.StringVar(value="-")
        self.obs_workflow_favorite_buttons = {}
        self.obs_workflow_live_scene_var = ctk.StringVar(value="LIVE SCENE  Unknown")
        self.obs_workflow_last_scene_control_var = ctk.StringVar(value="Last Scene Switch: -")
        self.obs_workflow_scene_rows = {}
        self.hide_timer = None
        self.quick_window = None
        self.thumbnail_refs = []
        self.preview_refs = []
        self.library_items = []
        self.selected_item = None
        self.editor_selected_banner = None
        self.editor_preview_refs = []
        self.editor_canvas_scale = 1.0
        self.editor_canvas_image = None
        self.editor_canvas_photo = None
        self.editor_canvas_banner_size = (1, 1)
        self.editor_drag_mode = None
        self.editor_drag_start = None
        self.editor_drag_original = None
        self.editor_sample_text = ctk.StringVar(value="HELLO WORLD")
        self.editor_font_family = ctk.StringVar(value="Bebas Neue")
        self.editor_font_size = ctk.IntVar(value=160)
        self.editor_text_color = ctk.StringVar(value="#FFFFFF")
        self.editor_stroke_color = ctk.StringVar(value="#000000")
        self.editor_stroke_width = ctk.IntVar(value=3)
        self.editor_uppercase = ctk.BooleanVar(value=True)
        self.banner_editor_controller = BannerEditorController(self)
        self.last_render_path = EXPORT_DIR / "caption_render.png"
        self.text_library_new_text = ctk.StringVar(value="")
        self.text_library_new_category = ctk.StringVar(value="")
        self.quick_cards_collapsed = set()
        self.live_card_pending_text = ""
        self.live_card_controller = LiveCardController(self)
        self.quick_cards_target_category = ctk.StringVar(value="Chat")
        self.quick_cards_editing_category = None
        self.quick_cards_editing_text = None
        self.quick_cards_edit_text_var = ctk.StringVar(value="")

        self.voice_enabled = ctk.BooleanVar(
            value=bool(self.config_data.get("voice_enabled", False))
        )
        self.voice_trigger_phrase = ctk.StringVar(
            value=str(self.config_data.get("voice_trigger_phrase", "live card"))
        )
        self.voice_culture = ctk.StringVar(
            value=str(self.config_data.get("voice_culture", "de-DE"))
        )
        self.voice_status_var = ctk.StringVar(value="OFF")
        self.voice_last_heard_var = ctk.StringVar(value="-")
        self.voice_process = None
        self.voice_reader_thread = None
        self.voice_stop_requested = False

        self.host = ctk.StringVar(value=self.config_data["host"])
        self.port = ctk.StringVar(value=self.config_data["port"])
        self.password = ctk.StringVar(value=self.config_data["password"])
        self.scene_name = ctk.StringVar(value=self.config_data["scene_name"])
        self.caption_group = ctk.StringVar(value=self.config_data["caption_group"])
        self.caption_text = ctk.StringVar(value=self.config_data["caption_text"])
        self.caption_banner_source = ctk.StringVar(value=self.config_data.get("caption_banner_source", "VADAFOK Caption Banner"))
        self.caption_render_source = ctk.StringVar(value=self.config_data.get("caption_render_source", "VADAFOK Caption Render"))
        self.scene_card_source = ctk.StringVar(value=self.config_data.get("scene_card_source", "VADAFOK Scene Card"))
        self.duration = ctk.StringVar(value=self.config_data["duration"])
        self.style = ctk.StringVar(value=self.config_data["style"])
        self.project_folder = ctk.StringVar(value=self.config_data.get("project_folder", ""))
        self.card_output_folder = ctk.StringVar(
            value=str(self.config_data.get("card_output_folder", "") or EXPORT_DIR)
        )
        self.card_batch_output_folder = ctk.StringVar(
            value=str(self.config_data.get("card_batch_output_folder", "") or EXPORT_DIR)
        )
        self.card_ask_output_location = ctk.BooleanVar(
            value=bool(self.config_data.get("card_ask_output_location", False))
        )
        self.sound_service = SoundService(self.project_folder.get())
        self.stream_effect_enabled = ctk.BooleanVar(
            value=bool(self.config_data.get("stream_effect_enabled", False))
        )
        self.stream_effect_source = ctk.StringVar(
            value=str(
                self.config_data.get(
                    "stream_effect_source",
                    "VADAFOK Stream Effect",
                )
            )
        )
        self.sound_favorite_buttons = []
        self._ensure_sound_favorites()
        self.library_section = ctk.StringVar(value="All")
        self.library_banner_picker_mode = False
        self.library_return_page = None
        self.library_controller = LibraryController(self)
        self.search_text = ctk.StringVar(value="")
        self.favorite_filter = ctk.BooleanVar(value=False)

        self.caption_engine = ctk.StringVar(value=self.config_data.get("caption_engine", "obs_text"))
        self.caption_font_family = ctk.StringVar(value=self.config_data.get("caption_font_family", "Bebas Neue"))
        self.caption_font_size = ctk.IntVar(value=int(self.config_data.get("caption_font_size", 160)))
        self.caption_text_color = ctk.StringVar(value=self.config_data.get("caption_text_color", "#FFFFFF"))
        self.caption_stroke_color = ctk.StringVar(value=self.config_data.get("caption_stroke_color", "#000000"))
        self.caption_stroke_width = ctk.IntVar(value=int(self.config_data.get("caption_stroke_width", 3)))
        self.caption_render_width = ctk.IntVar(value=int(self.config_data.get("caption_render_width", 1600)))
        self.caption_render_height = ctk.IntVar(value=int(self.config_data.get("caption_render_height", 260)))
        self.caption_uppercase = ctk.BooleanVar(value=bool(self.config_data.get("caption_uppercase", True)))
        self.caption_safe_left = ctk.IntVar(value=int(self.config_data.get("caption_safe_left", 12)))
        self.caption_safe_right = ctk.IntVar(value=int(self.config_data.get("caption_safe_right", 12)))
        self.caption_safe_top = ctk.IntVar(value=int(self.config_data.get("caption_safe_top", 24)))
        self.caption_safe_bottom = ctk.IntVar(value=int(self.config_data.get("caption_safe_bottom", 24)))

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.build_sidebar()
        self.show_library()
        self.bind_all("<F8>", lambda e: self.open_quick_caption())
        self.protocol("WM_DELETE_WINDOW", self.on_app_close)

        if self.voice_enabled.get():
            self.after(1000, self.start_voice_trigger)

    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#050505")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        ctk.CTkLabel(self.sidebar, text="🎭 VADAFOK", font=ctk.CTkFont(size=26, weight="bold"), text_color=GOLD).pack(anchor="w", padx=18, pady=(24, 0))
        ctk.CTkLabel(self.sidebar, text=SIDEBAR_VERSION, text_color="#BCA870").pack(anchor="w", padx=20, pady=(0, 22))
        self.nav_buttons = {}
        pages = [
            ("Library", self.show_library),
            ("Banner Editor", self.show_banner_profiles_page),
            ("Template Editor", self.show_template_editor_page),
            ("Card Creator", self.show_card_creator_page),
            ("Live Card", self.show_live_card),
            ("Caption Engine", self.show_caption_engine_page),
            ("Quick Cards", self.show_quick_cards),
            ("OBS Connection", self.show_obs_page),
            ("OBS Workflow", self.show_obs_workflow_page),
            ("Silent Director", self.show_silent_director_page),
            ("Settings", self.show_settings_page),
        ]
        for name, cmd in pages:
            btn = ctk.CTkButton(self.sidebar, text=name, height=42, corner_radius=10, anchor="w", fg_color="transparent", hover_color=GOLD_DARK, text_color=TEXT, command=cmd)
            btn.pack(fill="x", padx=14, pady=5)
            self.nav_buttons[name] = btn
        ctk.CTkFrame(self.sidebar, fg_color="transparent").pack(fill="both", expand=True)
        box = ctk.CTkFrame(self.sidebar, fg_color="#0D0D0D", corner_radius=12)
        box.pack(fill="x", padx=14, pady=16)
        ctk.CTkLabel(box, text="OBS Status", text_color="#BCA870").pack(anchor="w", padx=12, pady=(10, 0))
        self.status_label = ctk.CTkLabel(box, text="● Not connected", text_color="#D86A6A", font=ctk.CTkFont(weight="bold"))
        self.status_label.pack(anchor="w", padx=12, pady=(2, 10))
        ctk.CTkLabel(box, text="F8 = Quick Caption", text_color="#BCA870").pack(anchor="w", padx=12, pady=(0, 10))

    def set_active(self, name):
        self.active_page = name
        for n, b in self.nav_buttons.items():
            active = n == name
            b.configure(fg_color=GOLD if active else "transparent", text_color="#111111" if active else TEXT)

    def clear_main(self):
        if getattr(self, "silent_director_drag_active", False):
            try:
                self.unbind_all("<B1-Motion>")
                self.unbind_all("<ButtonRelease-1>")
            except Exception:
                pass
            self.silent_director_drag_active = False
            self.silent_director_drag_index = None
            self.silent_director_drop_index = None
        if hasattr(self, "main"):
            self.main.destroy()
        self.main = ctk.CTkFrame(self, fg_color=DARK, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

    def page_title(self, text):
        ctk.CTkLabel(self.main, text=text, font=ctk.CTkFont(size=28, weight="bold"), text_color=GOLD).grid(row=0, column=0, padx=28, pady=(24, 12), sticky="w")

    def open_library_section(self, section):
        return self.library_controller.open_section(section)

    def library_section_changed(self, section):
        self.open_library_section(section)

    def show_library_folder_overview(self):
        self.open_library_section("Folder Overview")

    def render_library_folder_overview(self):
        """Render folder choices without scanning or decoding thumbnails."""
        return render_folder_overview(self)

    def open_live_card_banner_picker(self):
        return self.live_card_controller.open_live_card_banner_picker()

    def return_to_live_card_from_library(self):
        return self.live_card_controller.return_to_live_card_from_library()

    def open_template_background_picker(self):
        self.library_controller.open_template_background_picker()

        # Runtime fallbacks remain on the app as well. This guarantees
        # correct return behavior even if older Library code resets one
        # of the controller compatibility attributes.
        self.library_template_background_picker_mode = True
        self.library_return_page = "Template Editor"

    def show_library(self):
        return show_library_page(self)


    def reload_library(self):
        return self.library_controller.reload_section()

    def item_key(self, item):
        return self.library_controller.item_key(item)

    def item_is_favorite(self, item):
        return self.library_controller.item_is_favorite(item)

    def item_tags(self, item):
        return self.library_controller.item_tags(item)

    def render_library_grid(self):
        return render_asset_grid(self)


    def make_thumb_label(self, parent, path):
        return make_thumbnail_label(self, parent, path)

    def select_library_item(self, item):
        return select_library_item(self, item)

    def library_item_double_click(self, item):
        self.select_library_item(item)
        self.default_selected_action()

    def default_selected_action(self):
        if not self.selected_item:
            messagebox.showwarning(
                "Library",
                "Bitte zuerst ein Asset auswählen."
            )
            return

        item = self.selected_item

        if item.section == "Banners":
            self.use_selected_as_caption_banner()
            return
        if item.section == "Live Cards":
            self.open_selected_live_card()
            return
        if item.section == "Templates":
            self.assign_selected_template_background()
            return
        if item.section == "Sounds":
            self.open_selected_file()
            return

        self.show_selected_scene_card()







    def template_set_background_path(self, path, refresh_canvas=True):
        """Set the template background without touching destroyed editor widgets."""
        if not path:
            return

        data, dest = set_background_from_file(
            self.template_selected_name,
            path,
        )
        self.template_working_data = data

        if refresh_canvas:
            canvas = getattr(self, "template_canvas", None)
            canvas_exists = False
            if canvas is not None:
                try:
                    canvas_exists = bool(canvas.winfo_exists())
                except Exception:
                    canvas_exists = False

            if canvas_exists:
                self.template_draw_canvas()
                try:
                    canvas.focus_set()
                except Exception:
                    pass

        return dest



    def assign_selected_template_background(self):
        """Apply the selected Library image and finish the picker safely."""
        item = getattr(self, "selected_item", None)
        if item is None:
            messagebox.showwarning(
                "Template Background",
                "Bitte zuerst ein Template-Bild auswählen.",
            )
            return

        if getattr(item, "kind", "") != "image":
            messagebox.showwarning(
                "Template Background",
                "Bitte ein Bild aus der Library auswählen.",
            )
            return

        controller = getattr(self, "library_controller", None)
        controller_return = bool(
            controller is not None
            and controller.is_template_background_picker
        )
        flag_return = bool(
            getattr(
                self,
                "library_template_background_picker_mode",
                False,
            )
        )
        page_return = (
            getattr(self, "library_return_page", None)
            == "Template Editor"
        )
        should_return = (
            controller_return
            or flag_return
            or page_return
        )

        # The Template Editor canvas was destroyed when the Library page opened.
        # Do not redraw that stale widget. The newly opened editor page will draw
        # the updated background on its fresh canvas.
        dest = self.template_set_background_path(
            item.path,
            refresh_canvas=not should_return,
        )

        if should_return:
            if controller is not None:
                controller.cancel_picker()
            else:
                self.library_template_background_picker_mode = False
                self.library_return_page = None

            self.show_template_editor_page()
            return dest

        messagebox.showinfo(
            "Template Background",
            (
                f"Hintergrundbild gespeichert:\n\n"
                f"Template: {self.template_selected_name}\n"
                f"Bild: {Path(item.path).name}"
            ),
        )
        return dest

    def use_selected_as_caption_banner(self):
        return library_use_actions.use_as_caption_banner(self)


    def show_selected_scene_card(self):
        return library_use_actions.show_as_scene_card(self)

    def open_selected_live_card(self):
        return library_use_actions.open_live_card(self)

    def toggle_selected_favorite(self):
        return library_asset_actions.toggle_favorite(self)

    def edit_selected_tags(self):
        return library_asset_actions.edit_tags(self)

    def open_selected_folder(self):
        return library_asset_actions.open_selected_folder(self)

    def open_selected_file(self):
        return library_asset_actions.open_selected_file(self)

    def copy_selected_path(self):
        return library_asset_actions.copy_selected_path(self)




    def show_banner_profiles_page(self):
        from .banner_editor.page import show_banner_profiles_page
        return show_banner_profiles_page(self)

    def editor_select_banner(self, item):
        return self.banner_editor_controller.editor_select_banner(item)

    def editor_profile(self):
        return self.banner_editor_controller.editor_profile()

    def editor_load_profile_values(self, profile):
        return self.banner_editor_controller.editor_load_profile_values(profile)

    def editor_apply_profile_values(self):
        return self.banner_editor_controller.editor_apply_profile_values()

    def editor_save_profile(self):
        return self.banner_editor_controller.editor_save_profile()

    def editor_reset_style(self):
        return self.banner_editor_controller.editor_reset_style()

    def editor_reset_area(self):
        return self.banner_editor_controller.editor_reset_area()

    def editor_draw_canvas(self, full_redraw=True):
        return self.banner_editor_controller.editor_draw_canvas(full_redraw)

    def editor_redraw_banner(self):
        return self.banner_editor_controller.editor_redraw_banner()

    def editor_update_overlay(self):
        return self.banner_editor_controller.editor_update_overlay()

    def _pil_to_png_bytes(self, image):
        return self.banner_editor_controller._pil_to_png_bytes(image)

    def editor_draw_sample_text(self, canvas, x1, y1, x2, y2):
        return self.banner_editor_controller.editor_draw_sample_text(canvas, x1, y1, x2, y2)

    def editor_handle_points(self, x1, y1, x2, y2):
        return self.banner_editor_controller.editor_handle_points(x1, y1, x2, y2)

    def editor_hit_test(self, x, y):
        return self.banner_editor_controller.editor_hit_test(x, y)

    def editor_mouse_motion(self, event):
        return self.banner_editor_controller.editor_mouse_motion(event)

    def editor_mouse_down(self, event):
        return self.banner_editor_controller.editor_mouse_down(event)

    def editor_mouse_drag(self, event):
        return self.banner_editor_controller.editor_mouse_drag(event)

    def editor_mouse_up(self, event):
        return self.banner_editor_controller.editor_mouse_up(event)

    def show_live_card_page(self):
        return self.live_card_controller.show_live_card_page()

    def live_card_current_banner_name(self):
        return self.live_card_controller.live_card_current_banner_name()

    def live_card_current_effect_name(self):
        return self.live_card_controller.live_card_current_effect_name()

    def _sync_sound_service_project(self):
        return self.live_card_controller._sync_sound_service_project()

    def default_sound_favorites(self):
        return self.live_card_controller.default_sound_favorites()

    def _ensure_sound_favorites(self):
        return self.live_card_controller._ensure_sound_favorites()

    def _apply_selected_sound_effect(self, relative):
        return self.live_card_controller._apply_selected_sound_effect(relative)

    def select_sound_favorite(self, index):
        return self.live_card_controller.select_sound_favorite(index)

    def refresh_sound_favorite_buttons(self):
        return self.live_card_controller.refresh_sound_favorite_buttons()

    def open_sound_favorites_editor(self):
        return self.live_card_controller.open_sound_favorites_editor()

    def change_live_card_effect(self):
        return self.live_card_controller.change_live_card_effect()

    def set_stream_effect_enabled(self):
        return self.live_card_controller.set_stream_effect_enabled()

    def preview_live_card_effect(self):
        return self.live_card_controller.preview_live_card_effect()

    def reset_live_card_text(self):
        return self.live_card_controller.reset_live_card_text()

    def show_live_card(self):
        return self.live_card_controller.show_live_card()

    def option(self, parent, label, values, var, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, padx=6, sticky="ew")
        ctk.CTkLabel(frame, text=label, text_color="#BCA870").pack(anchor="w")
        ctk.CTkOptionMenu(frame, values=values, variable=var, fg_color="#1A1A1A", button_color=GOLD_DARK, command=lambda _: self.update_preview()).pack(fill="x", pady=(6, 0))

    def show_caption_engine_page(self):
        self.set_active("Caption Engine")
        self.clear_main()
        self.page_title("Caption Engine")
        box = ctk.CTkFrame(self.main, fg_color=PANEL, corner_radius=18)
        box.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        fields = [
            ("Engine", self.caption_engine, ["obs_text", "smart_png"]),
            ("Font Family", self.caption_font_family, None),
            ("Font Size", self.caption_font_size, None),
            ("Text Color", self.caption_text_color, None),
            ("Stroke Color", self.caption_stroke_color, None),
            ("Stroke Width", self.caption_stroke_width, None),
            ("Render Width", self.caption_render_width, None),
            ("Render Height", self.caption_render_height, None),
            ("Safe Left %", self.caption_safe_left, None),
            ("Safe Right %", self.caption_safe_right, None),
            ("Safe Top %", self.caption_safe_top, None),
            ("Safe Bottom %", self.caption_safe_bottom, None),
        ]
        for label, var, values in fields:
            row = ctk.CTkFrame(box, fg_color="transparent")
            row.pack(fill="x", padx=24, pady=7)
            ctk.CTkLabel(row, text=label, width=150, anchor="w", text_color="#BCA870").pack(side="left")
            if values:
                ctk.CTkOptionMenu(row, values=values, variable=var).pack(side="left", fill="x", expand=True)
            else:
                ctk.CTkEntry(row, textvariable=var).pack(side="left", fill="x", expand=True)
        ctk.CTkCheckBox(box, text="Uppercase", variable=self.caption_uppercase, text_color=TEXT).pack(anchor="w", padx=24, pady=8)
        ctk.CTkLabel(box, text="Studio 2.8.6: smart_png rendert Banner + Text als fertige PNG. OBS braucht dafür nur die Bildquelle 'VADAFOK Caption Render'.", text_color="#D9C58C", wraplength=780, justify="left").pack(anchor="w", padx=24, pady=12)
        ctk.CTkButton(box, text="SAVE SETTINGS", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=self.save_config).pack(anchor="w", padx=24, pady=12)



    def template_selected_field_data(self):
        template = self.template_current()
        if self.template_selected_field is None:
            return None
        if 0 <= self.template_selected_field < len(template["fields"]):
            return template["fields"][self.template_selected_field]
        return None

    def template_load_selected_properties(self):
        field = self.template_selected_field_data()
        if not field:
            self.template_prop_name.set("")
            self.template_prop_font_family.set("")
            self.template_prop_font_size.set(90)
            self.template_prop_text_color.set("#FFFFFF")
            self.template_prop_stroke_color.set("#000000")
            self.template_prop_stroke_width.set(3)
            self.template_prop_uppercase.set(True)
            return

        self.template_prop_name.set(field.get("name", "field"))
        self.template_prop_font_family.set(field.get("font_family", "Bebas Neue"))
        self.template_prop_font_size.set(int(field.get("font_size", 90)))
        self.template_prop_text_color.set(field.get("text_color", "#FFFFFF"))
        self.template_prop_stroke_color.set(field.get("stroke_color", "#000000"))
        self.template_prop_stroke_width.set(int(field.get("stroke_width", 3)))
        self.template_prop_uppercase.set(bool(field.get("uppercase", True)))

    def template_apply_selected_properties(self):
        field = self.template_selected_field_data()
        if not field:
            return
        try:
            field["name"] = self.template_prop_name.get() or "field"
            field["font_family"] = self.template_prop_font_family.get() or "Bebas Neue"
            field["font_size"] = int(self.template_prop_font_size.get())
            field["text_color"] = self.template_prop_text_color.get() or "#FFFFFF"
            field["stroke_color"] = self.template_prop_stroke_color.get() or "#000000"
            field["stroke_width"] = int(self.template_prop_stroke_width.get())
            field["uppercase"] = bool(self.template_prop_uppercase.get())

            # Property changes affect only field overlays. Avoid a complete canvas,
            # background, status, and Layers rebuild for every key release.
            self.template_update_fields_overlay(
                refresh_layers=False,
                refresh_status=False,
            )
            self.template_schedule_property_commit()
        except Exception:
            pass

    def template_schedule_property_commit(self, delay_ms=250):
        """Debounce property persistence and the dependent Layers/status refresh."""
        pending = getattr(self, "template_property_commit_job", None)
        if pending is not None:
            try:
                self.after_cancel(pending)
            except Exception:
                pass

        try:
            self.template_property_commit_job = self.after(
                int(delay_ms),
                self.template_commit_selected_properties,
            )
        except Exception:
            self.template_commit_selected_properties()

    def template_commit_selected_properties(self):
        self.template_property_commit_job = None
        try:
            save_template(self.template_selected_name, self.template_current())
        except Exception:
            return

        # The field name may be displayed in Layers and status. Refresh those once
        # after typing pauses instead of rebuilding them for every character.
        self.template_update_fields_overlay(
            refresh_layers=True,
            refresh_status=True,
        )




    def template_background_status(self):
        template = self.template_current()
        bg = template.get("background", "")
        if not bg:
            return "kein Hintergrund"
        return f"{Path(bg).name} ({'OK' if Path(bg).exists() else 'FEHLT'})"





    def template_choose_background_file(self):
        path = filedialog.askopenfilename(
            title="Template Hintergrund auswählen",
            filetypes=[
                ("Image files", "*.png *.jpg *.jpeg *.webp"),
                ("PNG files", "*.png"),
                ("All files", "*.*"),
            ],
        )
        if not path:
            return
        self.template_set_background_path(path)
        messagebox.showinfo("Template Background", f"Hintergrund gesetzt:\n{Path(path).name}")



    def template_set_background_from_selected(self):
        self.library_controller.open_template_background_picker()
    def template_clear_background(self):
        template = self.template_current()
        template["background"] = "background.png"
        save_template(self.template_selected_name, template)
        self.template_draw_canvas()
        messagebox.showinfo("Template Background", "Hintergrund entfernt.")



    def template_delete_current(self):
        names = list_templates()
        if not names:
            return
        name = self.template_selected_name
        if not messagebox.askyesno("Template löschen", f"Template wirklich löschen?\n\n{name}"):
            return
        try:
            delete_template(name)
            if hasattr(self, 'card_selected_template') and self.card_selected_template.get() == name:
                self.card_selected_template.set('')
        except Exception as e:
            messagebox.showerror("Template löschen", str(e))
            return

        names = list_templates()
        if names:
            default_name = get_default_template()
            self.template_selected_name = default_name if default_name in names else names[0]
            self.template_working_data = load_template(self.template_selected_name)
        else:
            data = create_template("Default Stream Plan")
            self.template_selected_name = data["name"]
            self.template_working_data = data

        self.template_selected_field = None
        self.template_selected_fields = set()
        self.show_template_editor_page()

    def template_duplicate_current(self):
        try:
            data = duplicate_template(self.template_selected_name)
            self.template_selected_name = data["name"]
            self.template_working_data = data
            self.template_selected_field = None
            self.show_template_editor_page()
        except Exception as e:
            messagebox.showerror("Template duplizieren", str(e))


    def ask_template_name_dialog(self, title, initial_value):
        result = {"value": None}

        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("520x210")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        dialog.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            dialog,
            text=title,
            text_color=GOLD,
            font=ctk.CTkFont(size=22, weight="bold")
        ).grid(row=0, column=0, padx=24, pady=(24, 8), sticky="w")

        ctk.CTkLabel(
            dialog,
            text="Neuer Name",
            text_color="#BCA870",
            font=ctk.CTkFont(size=14)
        ).grid(row=1, column=0, padx=24, pady=(0, 4), sticky="w")

        entry = ctk.CTkEntry(dialog, height=42, font=ctk.CTkFont(size=18))
        entry.grid(row=2, column=0, padx=24, pady=(0, 18), sticky="ew")
        entry.insert(0, initial_value or "")
        entry.focus_set()
        entry.select_range(0, "end")

        buttons = ctk.CTkFrame(dialog, fg_color="transparent")
        buttons.grid(row=3, column=0, padx=24, pady=(0, 24), sticky="ew")
        buttons.grid_columnconfigure(0, weight=1)
        buttons.grid_columnconfigure(1, weight=1)

        def save():
            value = entry.get().strip()
            if value:
                result["value"] = value
                dialog.destroy()

        def cancel():
            result["value"] = None
            dialog.destroy()

        ctk.CTkButton(
            buttons,
            text="Speichern",
            height=38,
            fg_color=GOLD,
            text_color="#111111",
            hover_color=GOLD_DARK,
            command=save
        ).grid(row=0, column=0, padx=(0, 8), sticky="ew")

        ctk.CTkButton(
            buttons,
            text="Abbrechen",
            height=38,
            fg_color="#333333",
            hover_color="#444444",
            command=cancel
        ).grid(row=0, column=1, padx=(8, 0), sticky="ew")

        dialog.bind("<Return>", lambda _e: save())
        dialog.bind("<Escape>", lambda _e: cancel())

        self.wait_window(dialog)
        return result["value"]


    def template_rename_current(self):
        new_name = self.ask_template_name_dialog(
            "Template umbenennen",
            self.template_selected_name
        )
        if not new_name:
            return
        new_name = new_name.strip()
        if not new_name:
            return
        try:
            was_default = get_default_template() == self.template_selected_name
            data = rename_template(self.template_selected_name, new_name)
            self.template_selected_name = data["name"]
            self.template_working_data = data
            if was_default:
                set_default_template(self.template_selected_name)
            self.show_template_editor_page()
        except Exception as e:
            messagebox.showerror("Template umbenennen", str(e))

    def template_set_current_default(self):
        if not self.template_selected_name:
            return
        set_default_template(self.template_selected_name)
        messagebox.showinfo("Default Template", f"Als Default gesetzt:\n{self.template_selected_name}")
        self.show_template_editor_page()



    def template_set_zoom(self, value):
        try:
            value = float(value)
        except Exception:
            value = 1.0
        self.template_zoom_factor = max(0.25, min(4.0, value))
        if hasattr(self, "template_zoom_label_var"):
            self.template_zoom_label_var.set(f"{int(self.template_zoom_factor * 100)}%")
        if hasattr(self, "template_canvas"):
            self.template_draw_canvas(refresh_layers=False)

    def template_zoom_in(self):
        self.template_set_zoom(getattr(self, "template_zoom_factor", 1.0) * 1.25)

    def template_zoom_out(self):
        self.template_set_zoom(getattr(self, "template_zoom_factor", 1.0) / 1.25)

    def template_zoom_reset(self):
        self.template_pan_x = 0
        self.template_pan_y = 0
        self.template_set_zoom(1.0)

    def template_mouse_wheel_zoom(self, event):
        ctrl_pressed = bool(getattr(event, "state", 0) & 0x0004)
        if not ctrl_pressed:
            return
        delta = getattr(event, "delta", 0)
        if delta > 0 or getattr(event, "num", None) == 4:
            self.template_zoom_in()
        elif delta < 0 or getattr(event, "num", None) == 5:
            self.template_zoom_out()
        return "break"



    def template_pan_start_drag(self, event):
        self.template_marquee_clear()
        self.template_clear_smart_guides()
        self.template_pan_active = True
        self.template_pan_start = (event.x, event.y)
        self.template_pan_origin = (
            int(getattr(self, "template_pan_x", 0)),
            int(getattr(self, "template_pan_y", 0))
        )
        try:
            self.template_canvas.configure(cursor="fleur")
        except Exception:
            pass
        return "break"

    def template_pan_drag(self, event):
        if not getattr(self, "template_pan_active", False):
            return "break"
        if not self.template_pan_start or not self.template_pan_origin:
            return "break"

        old_x = int(getattr(self, "template_pan_x", 0))
        old_y = int(getattr(self, "template_pan_y", 0))

        dx_total = event.x - self.template_pan_start[0]
        dy_total = event.y - self.template_pan_start[1]

        new_x = self.template_pan_origin[0] + dx_total
        new_y = self.template_pan_origin[1] + dy_total

        move_dx = new_x - old_x
        move_dy = new_y - old_y

        self.template_pan_x = new_x
        self.template_pan_y = new_y

        # Anti-flicker: do not redraw/reload the background image while panning.
        # Move all existing canvas items instead.
        if hasattr(self, "template_canvas") and (move_dx or move_dy):
            self.template_canvas.move("all", move_dx, move_dy)

        # Keep coordinate system in sync for hit testing and field editing.
        if hasattr(self, "template_canvas_offset"):
            ox, oy = self.template_canvas_offset
            self.template_canvas_offset = (ox + move_dx, oy + move_dy)

        return "break"

    def template_pan_end_drag(self, event=None):
        self.template_pan_active = False
        self.template_pan_start = None
        self.template_pan_origin = None
        self.template_smart_guides_enabled = ctk.BooleanVar(value=True)
        self.template_smart_snap_enabled = ctk.BooleanVar(value=True)
        self.template_smart_guide_tolerance = 8
        try:
            self.template_canvas.configure(cursor="")
        except Exception:
            pass
        # No redraw here. Current canvas items were moved in-place during pan.
        return "break"

    def template_pan_reset(self):
        self.template_pan_x = 0
        self.template_pan_y = 0
        if hasattr(self, "template_canvas"):
            self.template_draw_canvas(refresh_layers=False)



    def template_key_down(self, event):
        key = getattr(event, "keysym", "")
        if key in ("Shift_L", "Shift_R"):
            self.template_shift_down = True
        if key in ("Control_L", "Control_R"):
            self.template_ctrl_down = True

    def template_key_up(self, event):
        key = getattr(event, "keysym", "")
        if key in ("Shift_L", "Shift_R"):
            self.template_shift_down = False
        if key in ("Control_L", "Control_R"):
            self.template_ctrl_down = False

    def template_multi_select_modifier(self, event):
        return selection_controller.multi_select_modifier(self, event)



    def template_selected_indices(self):
        template = self.template_current()
        count = len(template.get("fields", []))
        selected = set(getattr(self, "template_selected_fields", set()))
        if self.template_selected_field is not None:
            selected.add(self.template_selected_field)
        return sorted(idx for idx in selected if 0 <= idx < count and not template.get('fields', [])[idx].get('hidden', False))

    def template_align_selected(self, mode):
        self.template_push_history('align')
        template = self.template_current()
        fields = template.get("fields", [])
        selected = self.template_selected_unlocked_indices() if hasattr(self, "template_selected_unlocked_indices") else self.template_selected_indices()

        if len(selected) < 2:
            messagebox.showwarning("Template Editor", "Bitte mindestens zwei Felder auswählen.")
            return

        selected_fields = [fields[i] for i in selected]

        left = min(int(f.get("x", 0)) for f in selected_fields)
        right = max(int(f.get("x", 0)) + int(f.get("width", 0)) for f in selected_fields)
        top = min(int(f.get("y", 0)) for f in selected_fields)
        bottom = max(int(f.get("y", 0)) + int(f.get("height", 0)) for f in selected_fields)
        center_x = (left + right) // 2
        center_y = (top + bottom) // 2

        for f in selected_fields:
            w = int(f.get("width", 0))
            h = int(f.get("height", 0))

            if mode == "left":
                f["x"] = left
            elif mode == "center":
                f["x"] = center_x - w // 2
            elif mode == "right":
                f["x"] = right - w
            elif mode == "top":
                f["y"] = top
            elif mode == "middle":
                f["y"] = center_y - h // 2
            elif mode == "bottom":
                f["y"] = bottom - h

        save_template(self.template_selected_name, template)
        self.template_draw_canvas()

    def template_distribute_selected(self, axis):
        self.template_push_history('distribute')
        template = self.template_current()
        fields = template.get("fields", [])
        selected = self.template_selected_unlocked_indices() if hasattr(self, "template_selected_unlocked_indices") else self.template_selected_indices()

        if len(selected) < 3:
            messagebox.showwarning("Template Editor", "Zum Verteilen bitte mindestens drei Felder auswählen.")
            return

        selected_fields = [fields[i] for i in selected]

        if axis == "horizontal":
            selected_fields.sort(key=lambda f: int(f.get("x", 0)))
            first = selected_fields[0]
            last = selected_fields[-1]
            start = int(first.get("x", 0))
            end = int(last.get("x", 0))
            if len(selected_fields) > 1:
                step = (end - start) / (len(selected_fields) - 1)
                for i, f in enumerate(selected_fields):
                    f["x"] = int(round(start + step * i))

        elif axis == "vertical":
            selected_fields.sort(key=lambda f: int(f.get("y", 0)))
            first = selected_fields[0]
            last = selected_fields[-1]
            start = int(first.get("y", 0))
            end = int(last.get("y", 0))
            if len(selected_fields) > 1:
                step = (end - start) / (len(selected_fields) - 1)
                for i, f in enumerate(selected_fields):
                    f["y"] = int(round(start + step * i))

        save_template(self.template_selected_name, template)
        self.template_draw_canvas()



    def template_keyboard_move_selected(self, dx, dy):
        self.template_push_history('keyboard move')
        template = self.template_current()
        fields = template.get("fields", [])
        selected = self.template_selected_unlocked_indices() if hasattr(self, "template_selected_unlocked_indices") else (self.template_selected_indices() if hasattr(self, "template_selected_indices") else [])

        if not selected:
            return "break"

        design_w, design_h = getattr(self, "template_canvas_design_size", (1280, 720))

        # Keep whole selected group within bounds.
        originals = [fields[i] for i in selected]
        min_dx = max(-int(f.get("x", 0)) for f in originals)
        min_dy = max(-int(f.get("y", 0)) for f in originals)
        max_dx = min(design_w - (int(f.get("x", 0)) + int(f.get("width", 0))) for f in originals)
        max_dy = min(design_h - (int(f.get("y", 0)) + int(f.get("height", 0))) for f in originals)

        dx = max(min_dx, min(max_dx, int(dx)))
        dy = max(min_dy, min(max_dy, int(dy)))

        for idx in selected:
            fields[idx]["x"] = int(fields[idx].get("x", 0)) + dx
            fields[idx]["y"] = int(fields[idx].get("y", 0)) + dy

        save_template(self.template_selected_name, template)
        self.template_update_fields_overlay()
        return "break"

    def template_keyboard_select_all(self):
        template = self.template_current()
        self.template_selected_fields = set(range(len(template.get("fields", []))))
        self.template_selected_field = next(iter(self.template_selected_fields), None) if self.template_selected_fields else None
        self.template_update_fields_overlay()
        return "break"

    def template_keyboard_clear_selection(self):
        self.template_clear_selection()
        self.template_load_selected_properties()
        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()
        self.template_update_fields_overlay()
        return "break"

    def template_keyboard_delete_selected(self):
        self.template_delete_field()
        return "break"

    def template_keyboard_duplicate_selected(self):
        self.template_copy_field()
        return "break"


    def template_shortcuts_allowed(self, event=None):
        # Template shortcuts must only work while the Template Editor page is active.
        try:
            if getattr(self, "active_page", None) != "Template Editor":
                return False
        except Exception:
            pass

        # Do not steal Delete/Backspace/Ctrl+A/etc. from text input widgets.
        widget = getattr(event, "widget", None) if event is not None else None
        try:
            widget_class = widget.winfo_class() if widget is not None else ""
        except Exception:
            widget_class = ""

        blocked_classes = {
            "Entry",
            "Text",
            "Spinbox",
            "TEntry",
            "TCombobox",
            "CTkEntry",
            "CTkTextbox",
            "CTkComboBox",
        }

        if widget_class in blocked_classes:
            return False

        # CustomTkinter wraps widgets; class names vary, so also check repr/name.
        widget_text = str(widget).lower() if widget is not None else ""
        if any(token in widget_text for token in ("entry", "textbox", "text", "combobox")):
            return False

        return True


    def template_keyboard_handler(self, event):
        if not self.template_shortcuts_allowed(event):
            return None

        key = getattr(event, "keysym", "")
        state = int(getattr(event, "state", 0) or 0)
        ctrl = bool(state & 0x0004) or bool(getattr(self, "template_ctrl_down", False))
        shift = bool(state & 0x0001) or bool(getattr(self, "template_shift_down", False))

        if ctrl and key.lower() == "z":
            return self.template_undo()

        if ctrl and key.lower() == "y":
            return self.template_redo()

        if ctrl and key.lower() == "a":
            return self.template_keyboard_select_all()

        if ctrl and key.lower() == "d":
            return self.template_keyboard_duplicate_selected()

        if key in ("Delete", "BackSpace"):
            return self.template_keyboard_delete_selected()

        if key == "Escape":
            return self.template_keyboard_clear_selection()

        step = 10 if shift else 1

        if key == "Left":
            return self.template_keyboard_move_selected(-step, 0)
        if key == "Right":
            return self.template_keyboard_move_selected(step, 0)
        if key == "Up":
            return self.template_keyboard_move_selected(0, -step)
        if key == "Down":
            return self.template_keyboard_move_selected(0, step)

        return None



    def template_snapshot(self):
        import copy
        return copy.deepcopy(self.template_current())

    def template_push_history(self, reason="edit"):
        import copy
        if not hasattr(self, "template_undo_stack"):
            self.template_undo_stack = []
        if not hasattr(self, "template_redo_stack"):
            self.template_redo_stack = []

        snapshot = copy.deepcopy(self.template_current())

        if self.template_undo_stack and self.template_undo_stack[-1] == snapshot:
            return

        self.template_undo_stack.append(snapshot)
        limit = int(getattr(self, "template_history_limit", 80))
        if len(self.template_undo_stack) > limit:
            self.template_undo_stack = self.template_undo_stack[-limit:]

        self.template_redo_stack.clear()

    def template_restore_snapshot(self, snapshot):
        import copy
        self.template_working_data = copy.deepcopy(snapshot)
        save_template(self.template_selected_name, self.template_working_data)

        # Clean selection if fields count changed.
        count = len(self.template_working_data.get("fields", []))
        self.template_selected_fields = {i for i in getattr(self, "template_selected_fields", set()) if 0 <= i < count}
        if self.template_selected_field is not None and not (0 <= self.template_selected_field < count):
            self.template_selected_field = next(iter(self.template_selected_fields), None) if self.template_selected_fields else None

        self.template_draw_canvas()
        self.template_load_selected_properties()
        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()

    def template_undo(self):
        import copy
        if not getattr(self, "template_undo_stack", []):
            return "break"

        current = copy.deepcopy(self.template_current())
        previous = self.template_undo_stack.pop()
        self.template_redo_stack.append(current)
        self.template_restore_snapshot(previous)
        return "break"

    def template_redo(self):
        import copy
        if not getattr(self, "template_redo_stack", []):
            return "break"

        current = copy.deepcopy(self.template_current())
        nxt = self.template_redo_stack.pop()
        self.template_undo_stack.append(current)
        self.template_restore_snapshot(nxt)
        return "break"





    def template_is_field_hidden(self, idx):
        template = self.template_current()
        fields = template.get("fields", [])
        if not (0 <= idx < len(fields)):
            return False
        return bool(fields[idx].get("hidden", False))

    def template_toggle_field_hidden(self, idx):
        template = self.template_current()
        fields = template.get("fields", [])
        if not (0 <= idx < len(fields)):
            return

        if hasattr(self, "template_push_history"):
            self.template_push_history("toggle visibility")

        fields[idx]["hidden"] = not bool(fields[idx].get("hidden", False))

        # Hidden fields should not stay selected.
        if fields[idx]["hidden"]:
            if hasattr(self, "template_selected_fields"):
                self.template_selected_fields.discard(idx)
            if self.template_selected_field == idx:
                self.template_selected_field = next(iter(getattr(self, "template_selected_fields", set())), None)

        save_template(self.template_selected_name, template)
        self.template_draw_canvas()
        self.template_build_layers_panel()
        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()


    def template_is_field_locked(self, idx):
        template = self.template_current()
        fields = template.get("fields", [])
        if not (0 <= idx < len(fields)):
            return False
        return bool(fields[idx].get("locked", False))

    def template_toggle_field_lock(self, idx):
        template = self.template_current()
        fields = template.get("fields", [])
        if not (0 <= idx < len(fields)):
            return

        if hasattr(self, "template_push_history"):
            self.template_push_history("toggle lock")

        fields[idx]["locked"] = not bool(fields[idx].get("locked", False))
        save_template(self.template_selected_name, template)

        # If the field was selected and is now locked, keep selection visible but prevent movement.
        self.template_update_fields_overlay()
        self.template_build_layers_panel()

    def template_selected_unlocked_indices(self):
        selected = self.template_selected_indices() if hasattr(self, "template_selected_indices") else []
        return [idx for idx in selected if not self.template_is_field_locked(idx)]



    def template_new_id(self):
        import uuid
        return str(uuid.uuid4())

    def template_ensure_field_ids(self):
        template = self.template_current()
        changed = False
        seen = set()

        for field in template.get("fields", []):
            fid = field.get("id")
            if not fid or fid in seen:
                field["id"] = self.template_new_id()
                changed = True
            seen.add(field["id"])

        template.setdefault("groups", [])

        if changed:
            save_template(self.template_selected_name, template)

    def template_field_id(self, idx):
        self.template_ensure_field_ids()
        template = self.template_current()
        fields = template.get("fields", [])
        if not (0 <= idx < len(fields)):
            return None
        return fields[idx].get("id")

    def template_index_by_field_id(self, field_id):
        self.template_ensure_field_ids()
        template = self.template_current()
        for idx, field in enumerate(template.get("fields", [])):
            if field.get("id") == field_id:
                return idx
        return None

    def template_groups(self):
        self.template_ensure_field_ids()
        template = self.template_current()
        return template.setdefault("groups", [])

    def template_clean_groups(self):
        self.template_ensure_field_ids()
        template = self.template_current()
        valid_ids = {field.get("id") for field in template.get("fields", []) if field.get("id")}
        clean = []

        for group in template.get("groups", []):
            field_ids = []
            for fid in group.get("field_ids", []):
                if fid in valid_ids and fid not in field_ids:
                    field_ids.append(fid)

            # Migrate old index-based groups if found.
            if not field_ids and group.get("fields"):
                for idx in group.get("fields", []):
                    fid = self.template_field_id(idx)
                    if fid and fid not in field_ids:
                        field_ids.append(fid)

            if field_ids:
                group["field_ids"] = field_ids
                group.pop("fields", None)
                group.setdefault("id", self.template_new_id())
                group.setdefault("name", "Group")
                clean.append(group)

        template["groups"] = clean

    def template_group_for_field(self, idx):
        self.template_clean_groups()
        fid = self.template_field_id(idx)
        if not fid:
            return None
        for group in self.template_groups():
            if fid in group.get("field_ids", []):
                return group
        return None

    def template_group_name_for_field(self, idx):
        group = self.template_group_for_field(idx)
        return group.get("name", "") if group else ""

    def template_selected_group_ids(self):
        ids = set()
        for idx in self.template_selected_indices() if hasattr(self, "template_selected_indices") else []:
            group = self.template_group_for_field(idx)
            if group:
                ids.add(group.get("id"))
        return ids



    def template_cancel_inline_rename(self, event=None):
        try:
            if self.template_rename_entry is not None:
                self.template_rename_entry.destroy()
        except Exception:
            pass
        self.template_rename_entry = None
        self.template_renaming_kind = None
        self.template_renaming_target = None
        self.template_build_layers_panel()
        return "break"

    def template_commit_inline_rename(self, event=None):
        if self.template_rename_entry is None:
            return "break"

        value = self.template_rename_entry.get().strip()
        kind = self.template_renaming_kind
        target = self.template_renaming_target

        try:
            self.template_rename_entry.destroy()
        except Exception:
            pass

        self.template_rename_entry = None
        self.template_renaming_kind = None
        self.template_renaming_target = None

        if not value:
            self.template_build_layers_panel()
            return "break"

        template = self.template_current()

        if kind == "group":
            group = self.template_find_group(target)
            if group and group.get("name") != value:
                if hasattr(self, "template_push_history"):
                    self.template_push_history("rename group")
                group["name"] = value
                save_template(self.template_selected_name, template)

        elif kind == "field":
            idx = target
            fields = template.get("fields", [])
            if idx is not None and 0 <= idx < len(fields) and fields[idx].get("name") != value:
                if hasattr(self, "template_push_history"):
                    self.template_push_history("rename field")
                fields[idx]["name"] = value
                save_template(self.template_selected_name, template)
                if idx == self.template_selected_field:
                    self.template_load_selected_properties()
                    if hasattr(self, "template_props_body"):
                        self.template_build_properties_panel()

        self.template_draw_canvas()
        self.template_build_layers_panel()
        return "break"

    def template_start_inline_rename_group(self, group_id):
        template = self.template_current()
        group = self.template_find_group(group_id)
        old_name = group.get("name", "Group") if group else str(group_id)

        new_name = simpledialog.askstring("Rename Group", "New group name:", initialvalue=old_name)
        if not new_name:
            return
        new_name = new_name.strip()
        if not new_name or new_name == old_name:
            return

        if hasattr(self, "template_push_history"):
            self.template_push_history("rename group")

        changed = False
        for grp in template.get("groups", []):
            if grp.get("id") == group_id or grp.get("name") == old_name:
                grp["name"] = new_name
                changed = True

        for field in template.get("fields", []):
            if field.get("group") == old_name:
                field["group"] = new_name
                changed = True

        if changed:
            save_template(self.template_selected_name, template)
            self.template_draw_canvas()
            self.template_build_layers_panel()


    def template_start_inline_rename_field(self, idx):
        template = self.template_current()
        fields = template.get("fields", [])
        if not (0 <= idx < len(fields)) or not hasattr(self, "template_layers_body"):
            return

        self.template_cancel_inline_rename()
        self.template_renaming_kind = "field"
        self.template_renaming_target = idx

        entry = ctk.CTkEntry(self.template_layers_body)
        entry.insert(0, fields[idx].get("name", f"field_{idx+1}"))
        entry.grid(row=getattr(self, "_template_layer_row_for_field", {}).get(idx, 0), column=0, padx=(8, 4), pady=3, sticky="ew")
        entry.focus_set()
        entry.select_range(0, "end")
        entry.bind("<Return>", self.template_commit_inline_rename)
        entry.bind("<Escape>", self.template_cancel_inline_rename)
        entry.bind("<FocusOut>", self.template_commit_inline_rename)
        self.template_rename_entry = entry



    def template_group_is_collapsed(self, group_id):
        if not hasattr(self, "template_collapsed_groups"):
            self.template_collapsed_groups = set()
        return group_id in self.template_collapsed_groups

    def template_toggle_group_collapsed(self, group_id):
        if not hasattr(self, "template_collapsed_groups"):
            self.template_collapsed_groups = set()
        if group_id in self.template_collapsed_groups:
            self.template_collapsed_groups.remove(group_id)
        else:
            self.template_collapsed_groups.add(group_id)
        self.template_build_layers_panel()

    def template_field_is_in_collapsed_group(self, idx):
        try:
            group = self.template_group_for_field(idx)
            if not group:
                return False
            return self.template_group_is_collapsed(group.get("id"))
        except Exception:
            return False


    def template_find_group(self, group_id):
        for group in self.template_groups():
            if group.get("id") == group_id:
                return group
        return None

    def template_rename_group(self, group_id):
        self.template_start_inline_rename_group(group_id)


    def template_group_field_indices(self, group):
        indices = []
        template = self.template_current()
        fields = template.get("fields", [])
        for fid in group.get("field_ids", []):
            idx = self.template_index_by_field_id(fid)
            if idx is not None and 0 <= idx < len(fields):
                indices.append(idx)
        return indices

    def template_toggle_group_lock(self, group_id):
        group = self.template_find_group(group_id)
        if not group:
            return

        if hasattr(self, "template_push_history"):
            self.template_push_history("toggle group lock")

        new_state = not bool(group.get("locked", False))
        group["locked"] = new_state

        template = self.template_current()
        fields = template.get("fields", [])
        for idx in self.template_group_field_indices(group):
            fields[idx]["locked"] = new_state

        save_template(self.template_selected_name, template)
        self.template_update_fields_overlay()
        self.template_build_layers_panel()
        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()

    def template_toggle_group_hidden(self, group_id):
        group = self.template_find_group(group_id)
        if not group:
            return

        if hasattr(self, "template_push_history"):
            self.template_push_history("toggle group visibility")

        new_state = not bool(group.get("hidden", False))
        group["hidden"] = new_state

        template = self.template_current()
        fields = template.get("fields", [])
        for idx in self.template_group_field_indices(group):
            fields[idx]["hidden"] = new_state
            if new_state:
                if hasattr(self, "template_selected_fields"):
                    self.template_selected_fields.discard(idx)
                if self.template_selected_field == idx:
                    self.template_selected_field = None

        if self.template_selected_field is None and getattr(self, "template_selected_fields", set()):
            self.template_selected_field = next(iter(self.template_selected_fields), None)

        save_template(self.template_selected_name, template)
        self.template_draw_canvas()
        self.template_build_layers_panel()
        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()


    def template_select_group(self, group_id):
        self.template_clean_groups()
        template = self.template_current()
        group = next((g for g in template.get("groups", []) if g.get("id") == group_id), None)
        if not group:
            return

        selected = set()
        fields = template.get("fields", [])
        for fid in group.get("field_ids", []):
            idx = self.template_index_by_field_id(fid)
            if idx is not None and 0 <= idx < len(fields) and not fields[idx].get("hidden", False):
                selected.add(idx)

        self.template_selected_fields = selected
        self.template_selected_field = next(iter(selected), None) if selected else None
        self.template_load_selected_properties()
        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()
        self.template_update_fields_overlay()
        self.template_build_layers_panel()

    def template_create_group(self):
        self.template_ensure_field_ids()
        selected = self.template_selected_indices() if hasattr(self, "template_selected_indices") else []

        if len(selected) < 2:
            messagebox.showwarning("Template Editor", "Bitte mindestens zwei Felder auswählen.")
            return

        template = self.template_current()
        groups = template.setdefault("groups", [])

        selected_ids = [self.template_field_id(idx) for idx in selected]
        selected_ids = [fid for fid in selected_ids if fid]

        if len(selected_ids) < 2:
            messagebox.showwarning("Template Editor", "Für eine Gruppe sind mindestens zwei gültige Felder nötig.")
            return

        if hasattr(self, "template_push_history"):
            self.template_push_history("group fields")

        # Remove selected fields from existing groups so a field belongs to only one group.
        for group in groups:
            group["field_ids"] = [fid for fid in group.get("field_ids", []) if fid not in selected_ids]
            group.pop("fields", None)
        groups[:] = [g for g in groups if g.get("field_ids")]

        base = "Group"
        existing = {g.get("name", "") for g in groups}
        name = base
        n = 2
        while name in existing:
            name = f"{base} {n}"
            n += 1

        groups.append({
            "id": self.template_new_id(),
            "name": name,
            "field_ids": selected_ids,
            "locked": False,
            "hidden": False,
        })

        save_template(self.template_selected_name, template)
        self.template_update_fields_overlay()
        self.template_build_layers_panel()

    def template_ungroup_selected(self):
        self.template_clean_groups()
        selected = self.template_selected_indices() if hasattr(self, "template_selected_indices") else []
        selected_ids = {self.template_field_id(idx) for idx in selected}
        selected_ids.discard(None)

        group_ids = set()
        for group in self.template_groups():
            if selected_ids.intersection(set(group.get("field_ids", []))):
                group_ids.add(group.get("id"))

        if not group_ids:
            messagebox.showwarning("Template Editor", "Keine Gruppe ausgewählt.")
            return

        if hasattr(self, "template_push_history"):
            self.template_push_history("ungroup fields")

        template = self.template_current()
        template["groups"] = [g for g in template.get("groups", []) if g.get("id") not in group_ids]

        save_template(self.template_selected_name, template)
        self.template_update_fields_overlay()
        self.template_build_layers_panel()



    def template_layer_drag_start(self, event, idx):
        return layer_controller.layer_drag_start(self, event,idx)

    def template_layer_clear_drop_indicator(self):
        return layer_controller.layer_clear_drop_indicator(self)

    def template_layer_drag_motion(self, event):
        return layer_controller.layer_drag_motion(self, event)

    def template_layer_show_drop_indicator(self, target_idx):
        return layer_controller.layer_show_drop_indicator(self, target_idx)

    def template_layer_drag_end(self, event):
        return layer_controller.layer_drag_end(self, event)

    def template_layer_target_from_y(self, y_root):
        return layer_controller.layer_target_from_y(self, y_root)


    def template_move_layer_to_index(self, source_idx, target_idx):
        return layer_controller.move_layer_to_index(self, source_idx,target_idx)


    def template_build_layers_panel(self):
        return build_layers_panel(self)


    def template_refresh_layers_selection(self):
        return layer_controller.refresh_layers_selection(self)

    def template_refresh_selection_ui(self, refresh_properties=True):
        """Refresh selection-dependent UI while preserving the legacy contract."""
        if refresh_properties:
            self.template_load_selected_properties()
            self.template_build_properties_panel()
        self.template_update_fields_overlay(refresh_layers=False)
        self.template_refresh_layers_selection()

    def template_select_layer(self, idx):
        return layer_controller.select_layer(self, idx)

    def template_move_layer(self, idx, direction):
        return layer_controller.move_layer(self, idx,direction)



    def template_equal_spacing_selected(self, axis):
        template = self.template_current()
        fields = template.get("fields", [])

        selected = (
            self.template_selected_unlocked_indices()
            if hasattr(self, "template_selected_unlocked_indices")
            else (self.template_selected_indices() if hasattr(self, "template_selected_indices") else [])
        )

        selected = [
            idx for idx in selected
            if 0 <= idx < len(fields) and not fields[idx].get("hidden", False)
        ]

        if len(selected) < 3:
            messagebox.showwarning("Template Editor", "Equal Spacing braucht mindestens drei ungesperrte, sichtbare Felder.")
            return

        if hasattr(self, "template_push_history"):
            self.template_push_history("equal spacing")

        selected_fields = [fields[i] for i in selected]

        if axis == "horizontal":
            selected_fields.sort(key=lambda f: int(f.get("x", 0)))
            left = min(int(f.get("x", 0)) for f in selected_fields)
            right = max(int(f.get("x", 0)) + int(f.get("width", 0)) for f in selected_fields)
            total_width = sum(int(f.get("width", 0)) for f in selected_fields)
            gaps = len(selected_fields) - 1
            gap = (right - left - total_width) / gaps if gaps else 0

            cursor = left
            for f in selected_fields:
                f["x"] = int(round(cursor))
                cursor += int(f.get("width", 0)) + gap

        elif axis == "vertical":
            selected_fields.sort(key=lambda f: int(f.get("y", 0)))
            top = min(int(f.get("y", 0)) for f in selected_fields)
            bottom = max(int(f.get("y", 0)) + int(f.get("height", 0)) for f in selected_fields)
            total_height = sum(int(f.get("height", 0)) for f in selected_fields)
            gaps = len(selected_fields) - 1
            gap = (bottom - top - total_height) / gaps if gaps else 0

            cursor = top
            for f in selected_fields:
                f["y"] = int(round(cursor))
                cursor += int(f.get("height", 0)) + gap

        save_template(self.template_selected_name, template)
        self.template_draw_canvas()
        if hasattr(self, "template_layers_body"):
            self.template_build_layers_panel()



    def template_selected_style_indices(self):
        if hasattr(self, "template_selected_indices"):
            return self.template_selected_indices()
        selected = set(getattr(self, "template_selected_fields", set()))
        if self.template_selected_field is not None:
            selected.add(self.template_selected_field)
        template = self.template_current()
        count = len(template.get("fields", []))
        return sorted(i for i in selected if 0 <= i < count)

    def template_build_style_presets_panel(self):
        if not hasattr(self, "template_styles_body"):
            return

        for w in self.template_styles_body.winfo_children():
            w.destroy()

        styles = style_engine.list_styles()
        if not styles:
            ctk.CTkLabel(
                self.template_styles_body,
                text="Noch keine Styles gespeichert.",
                text_color="#777777",
                wraplength=170,
                justify="left"
            ).grid(row=0, column=0, columnspan=2, padx=8, pady=8, sticky="w")
            return

        for row, name in enumerate(styles):
            ctk.CTkButton(
                self.template_styles_body,
                text=name,
                anchor="w",
                fg_color="#171717",
                hover_color="#2C2C2C",
                text_color="#D9C58C",
                command=lambda n=name: self.template_apply_style_preset(n)
            ).grid(row=row, column=0, padx=(8, 4), pady=3, sticky="ew")

            ctk.CTkButton(
                self.template_styles_body,
                text="DEL",
                width=44,
                fg_color="#5A1F1F",
                hover_color="#7A2A2A",
                command=lambda n=name: self.template_delete_style_preset(n)
            ).grid(row=row, column=1, padx=(2, 8), pady=3, sticky="ew")

        self.template_styles_body.grid_columnconfigure(0, weight=1)

    def template_save_style_preset(self):
        indices = self.template_selected_style_indices()
        if not indices:
            messagebox.showwarning("Style Presets", "Bitte zuerst ein Feld auswählen.")
            return

        fields = self.template_current().get("fields", [])
        field = fields[indices[-1]]

        name = simpledialog.askstring("Save Style", "Style Name:")
        if not name:
            return
        name = name.strip()
        if not name:
            return

        try:
            existing = set(style_engine.list_styles())
            if name in existing:
                if not messagebox.askyesno("Style Presets", f"Style '{name}' existiert bereits. Überschreiben?"):
                    return

            path = style_engine.save_style(name, field)
            self.template_build_style_presets_panel()
            messagebox.showinfo("Style Presets", f"Style gespeichert:\n{path}")
        except Exception as e:
            messagebox.showerror("Style Presets", f"Style konnte nicht gespeichert werden:\n{e}")

    def template_apply_style_preset(self, name):
        indices = self.template_selected_style_indices()
        if not indices:
            messagebox.showwarning("Style Presets", "Bitte zuerst ein oder mehrere Felder auswählen.")
            return

        style = style_engine.load_style(name)
        if not style:
            messagebox.showwarning("Style Presets", "Dieser Style ist leer oder konnte nicht geladen werden.")
            return

        if hasattr(self, "template_push_history"):
            self.template_push_history("apply style preset")

        template = self.template_current()
        fields = template.get("fields", [])
        for idx in indices:
            if 0 <= idx < len(fields):
                style_engine.apply_style(fields[idx], style)

        save_template(self.template_selected_name, template)
        self.template_draw_canvas()
        self.template_load_selected_properties()
        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()
        if hasattr(self, "template_layers_body"):
            self.template_build_layers_panel()

    def template_delete_style_preset(self, name):
        if not messagebox.askyesno("Style Presets", f"Style '{name}' wirklich löschen?"):
            return
        style_engine.delete_style(name)
        self.template_build_style_presets_panel()


    def show_template_editor_page(self):
        return self.template_editor_controller.show_page()

    def template_refresh_template_list_selection(self):
        buttons = getattr(self, "template_list_buttons", {})
        available = sorted(list_templates())

        if set(buttons) != set(available):
            return False

        default_name = get_default_template()
        for name, button in buttons.items():
            prefix = "✓ " if name == self.template_selected_name else ""
            if name == default_name:
                prefix += "★ "
            try:
                button.configure(text=prefix + name)
            except Exception:
                return False

        return True

    def template_refresh_selected_template(self):
        self.template_refresh_template_list_selection()

        status_label = getattr(self, "template_status_label", None)
        if status_label is not None:
            try:
                status_label.configure(text=self.template_selected_name)
            except Exception:
                pass

        self.template_build_properties_panel()
        self.template_ensure_field_ids()
        self.template_draw_canvas()
        self.template_build_style_presets_panel()
        self.template_build_layers_panel()

    def template_build_properties_panel(self):
        return build_properties_panel(self)



    def template_current(self):
        names = list_templates()
        if not names:
            create_template("Default Stream Plan")
            names = list_templates()

        if self.template_selected_name not in names:
            self.template_selected_name = names[0]

        if self.template_working_data is None or self.template_working_data.get("name") != self.template_selected_name:
            self.template_working_data = load_template(self.template_selected_name)

        return self.template_working_data



    def template_create_default(self):
        data = create_template("New Template")
        self.template_selected_name = data["name"]
        self.template_working_data = data
        self.template_selected_field = None
        self.template_selected_fields = set()
        self.show_template_editor_page()


    def template_select(self, name):
        self.template_editor_controller.select_template(name)




    def template_save(self):
        template = self.template_current()
        save_template(self.template_selected_name, template)

        bg_ok, bg_msg = ensure_background_file(self.template_selected_name, template)

        if bg_ok:
            messagebox.showinfo(
                "Template Editor",
                f"Template gespeichert:\n{self.template_selected_name}\n\n✓ template.json gespeichert\n✓ {bg_msg}"
            )
        else:
            messagebox.showwarning(
                "Template Editor",
                f"Template gespeichert:\n{self.template_selected_name}\n\n✓ template.json gespeichert\n✗ {bg_msg}"
            )

        self.template_draw_canvas()


    def template_reset_default(self):
        # Reset fields but keep current template and background if present.
        current = self.template_current()
        bg = current.get("background", "background.png")
        fresh = create_default_template(self.template_selected_name)
        fresh["background"] = bg
        self.template_working_data = fresh
        save_template(self.template_selected_name, fresh)
        self.template_selected_field = None
        self.template_draw_canvas()


    def template_add_field(self):
        self.template_push_history('add field')
        template = self.template_current()
        name = f"field_{len(template['fields']) + 1}"
        template["fields"].append({
            "name": name,
            "x": 160,
            "y": 120 + len(template["fields"]) * 70,
            "width": 500,
            "height": 90,
            "font_family": "Bebas Neue",
            "font_size": 90,
            "text_color": "#FFFFFF",
            "stroke_color": "#000000",
            "stroke_width": 3,
            "uppercase": True
        })
        self.template_selected_field = len(template["fields"]) - 1
        self.template_load_selected_properties()
        save_template(self.template_selected_name, template)
        self.template_draw_canvas()



    def template_copy_field(self):
        self.template_push_history('copy field')
        template = self.template_current()
        fields = template.get("fields", [])

        selected = set(getattr(self, "template_selected_fields", set()))
        if self.template_selected_field is not None:
            selected.add(self.template_selected_field)
        selected = sorted(idx for idx in selected if 0 <= idx < len(fields))

        if not selected:
            messagebox.showwarning("Template Editor", "Bitte zuerst ein Feld auswählen.")
            return

        existing = {f.get("name", "") for f in fields}
        design_w, design_h = getattr(self, "template_canvas_design_size", (1280, 720))

        copied_indices = []
        src_to_copy_id = {}
        for src_idx in selected:
            source = dict(fields[src_idx])
            base_name = source.get("name", "field")

            candidate = f"{base_name}_copy"
            index = 2
            while candidate in existing:
                candidate = f"{base_name}_copy{index}"
                index += 1
            existing.add(candidate)

            copied = dict(source)
            copied["id"] = self.template_new_id()
            copied["name"] = candidate
            copied["x"] = min(max(0, int(copied.get("x", 0)) + 15), max(0, int(design_w) - int(copied.get("width", 100))))
            copied["y"] = min(max(0, int(copied.get("y", 0)) + 15), max(0, int(design_h) - int(copied.get("height", 50))))

            template.setdefault("fields", []).append(copied)
            new_idx = len(template["fields"]) - 1
            copied_indices.append(new_idx)
            src_to_copy_id[source.get("id")] = copied.get("id")

        # If a complete group was copied, recreate it for the copied fields.
        copied_source_ids = {fid for fid in src_to_copy_id.keys() if fid}
        for group in list(template.get("groups", [])):
            group_ids = set(group.get("field_ids", []))
            if group_ids and group_ids.issubset(copied_source_ids):
                base_name = group.get("name", "Group") + "_copy"
                existing_names = {g.get("name", "") for g in template.setdefault("groups", [])}
                name = base_name
                n = 2
                while name in existing_names:
                    name = f"{base_name}{n}"
                    n += 1
                template["groups"].append({
                    "id": self.template_new_id(),
                    "name": name,
                    "field_ids": [src_to_copy_id[fid] for fid in group.get("field_ids", []) if fid in src_to_copy_id],
                    "locked": bool(group.get("locked", False)),
                    "hidden": bool(group.get("hidden", False)),
                })

        self.template_selected_fields = set(copied_indices)
        self.template_selected_field = copied_indices[-1] if copied_indices else None

        save_template(self.template_selected_name, template)
        self.template_load_selected_properties()
        self.template_draw_canvas()

        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()

        try:
            if len(copied_indices) == 1 and hasattr(self, "template_prop_name_entry"):
                self.template_prop_name_entry.focus_set()
                self.template_prop_name_entry.select_range(0, "end")
        except Exception:
            pass


    def template_delete_field(self):
        self.template_push_history('delete field')
        template = self.template_current()
        fields = template.get("fields", [])

        selected = set(getattr(self, "template_selected_fields", set()))
        if self.template_selected_field is not None:
            selected.add(self.template_selected_field)

        selected = {idx for idx in selected if 0 <= idx < len(fields)}
        locked_selected = {idx for idx in selected if self.template_is_field_locked(idx)}
        selected = selected - locked_selected
        if locked_selected and not selected:
            messagebox.showwarning("Template Editor", "Auswahl enthält nur gesperrte Felder.")
            return
        if locked_selected:
            messagebox.showinfo("Template Editor", f"{len(locked_selected)} gesperrte Felder wurden nicht gelöscht.")
        if not selected:
            messagebox.showwarning("Template Editor", "Bitte zuerst ein Feld auswählen.")
            return

        if len(selected) > 1:
            if not messagebox.askyesno("Template Editor", f"{len(selected)} Felder wirklich löschen?"):
                return

        template["fields"] = [field for idx, field in enumerate(fields) if idx not in selected]
        self.template_clean_groups()
        self.template_clear_selection()
        save_template(self.template_selected_name, template)
        self.template_draw_canvas()
        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()


    def template_draw_canvas(self, refresh_layers=True):
        return draw_canvas(self, refresh_layers)


    def template_load_background_image(self, bg_path):
        """Load a Template background once and reuse it until the file changes."""
        path = Path(bg_path)
        try:
            stamp = path.stat().st_mtime_ns
        except OSError:
            stamp = None

        cache_key = (str(path.resolve()), stamp)
        if getattr(self, "template_bg_cache_key", None) != cache_key:
            self.template_bg_cache_image = load_rgba(path)
            self.template_bg_cache_key = cache_key

        return self.template_bg_cache_image


    def template_clear_fields_overlay(self):
        if not hasattr(self, "template_canvas"):
            return
        try:
            self.template_canvas.delete("template_overlay")
        except Exception:
            pass


    def template_clear_smart_guides(self):
        return smart_guides.clear_smart_guides(self)

    def template_screen_line_x(self, x):
        return smart_guides.screen_line_x(self, x)

    def template_screen_line_y(self, y):
        return smart_guides.screen_line_y(self, y)

    def template_field_edges(self, field):
        return smart_guides.field_edges(self, field)

    def template_smart_targets(self):
        return smart_guides.smart_targets(self)

    def template_draw_smart_guides(self, guides_x=None, guides_y=None):
        return smart_guides.draw_smart_guides(self, guides_x,guides_y)

    def template_apply_smart_snap(self, x, y, w, h, mode):
        return smart_guides.apply_smart_snap(self, x,y,w,h,mode)

    def template_smart_guides_changed(self):
        return smart_guides.smart_guides_changed(self)



    def template_sync_selection_set(self):
        return selection_controller.sync_selection_set(self)

    def template_selection_count(self):
        return selection_controller.selection_count(self)

    def template_clear_selection(self):
        return selection_controller.clear_selection(self)

    def template_set_single_selection(self, idx):
        return selection_controller.set_single_selection(self, idx)

    def template_toggle_selection(self, idx):
        return selection_controller.toggle_selection(self, idx)


    def template_update_fields_overlay(self, bg_info=None, refresh_layers=True, refresh_status=True):
        return update_fields_overlay(self, bg_info, refresh_layers, refresh_status)



    def template_field_screen_rect(self, field):
        ox, oy = self.template_canvas_offset
        s = self.template_canvas_scale
        x1 = ox + int(field["x"] * s)
        y1 = oy + int(field["y"] * s)
        x2 = ox + int((field["x"] + field["width"]) * s)
        y2 = oy + int((field["y"] + field["height"]) * s)
        return x1, y1, x2, y2

    def template_handle_points(self, x1, y1, x2, y2):
        return mouse_controller.handle_points(self, x1,y1,x2,y2)

    def template_draw_handles(self, canvas, x1, y1, x2, y2):
        for _name, hx, hy in self.template_handle_points(x1, y1, x2, y2):
            canvas.create_rectangle(
                hx - 6, hy - 6, hx + 6, hy + 6,
                fill=GOLD,
                outline="#111111"
            )

    def template_hit_test(self, x, y):
        return mouse_controller.hit_test(self, x,y)

    def template_cursor_for_mode(self, mode):
        return mouse_controller.cursor_for_mode(self, mode)

    def template_mouse_motion(self, event):
        return mouse_controller.mouse_motion(self, event)


    def template_marquee_clear(self):
        return selection_controller.marquee_clear(self)

    def template_marquee_start_select(self, event, add_mode=False):
        return selection_controller.marquee_start_select(self, event,add_mode)

    def template_marquee_drag(self, event):
        return selection_controller.marquee_drag(self, event)

    def template_marquee_finish(self, event):
        return selection_controller.marquee_finish(self, event)


    def template_mouse_down(self, event):
        return mouse_controller.mouse_down(self, event)


    def template_mouse_drag(self, event):
        return mouse_controller.mouse_drag(self, event)


    def template_mouse_up(self, event):
        return mouse_controller.mouse_up(self, event)



    def card_template_safe_name(self):
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in self.card_selected_template.get())

    def card_default_output_name(self):
        return f"card_{self.card_template_safe_name()}"

    def card_output_directory(self, batch=False):
        return self.card_export_controller.output_directory(batch=batch)

    def card_output_path(self, final=False, output_dir=None):
        return self.card_export_controller.output_path(
            final=final, output_dir=output_dir
        )

    def card_choose_final_output_path(self):
        return self.card_export_controller.choose_final_output_path()

    def card_choose_batch_output_directory(self):
        return self.card_export_controller.choose_batch_output_directory()

    def card_preview_changed(self, *_args):
        return self.card_preview_controller.changed(*_args)

    def card_clear_values(self):
        return self.card_data_controller.clear_values()

    def card_open_export_folder(self):
        return self.card_export_controller.open_export_folder()

    def card_copy_last_path(self):
        return self.card_export_controller.copy_last_path()



    def card_current_data_snapshot(self):
        return self.card_data_controller.current_snapshot()

    def card_apply_data_snapshot(self, snapshot):
        return self.card_data_controller.apply_snapshot(snapshot)

    def card_push_data_history(self):
        return self.card_data_controller.push_history()

    def card_undo_data(self):
        return self.card_data_controller.undo()

    def card_redo_data(self):
        return self.card_data_controller.redo()



    def card_template_field_index_by_name(self, field_name):
        return self.card_style_controller.field_index_by_name(field_name)

    def card_apply_style_to_field(self, field_name, style_name):
        return self.card_style_controller.apply_to_field(field_name, style_name)

    def card_open_template_editor_for_styles(self):
        return self.card_style_controller.open_template_editor()

    def card_batch_current_item_name(self):
        return self.card_batch_controller.current_item_name()

    def card_batch_add_current(self):
        return self.card_batch_controller.add_current()

    def card_batch_duplicate_selected(self):
        return self.card_batch_controller.duplicate_selected()

    def card_batch_remove_selected(self):
        return self.card_batch_controller.remove_selected()

    def card_batch_clear(self):
        return self.card_batch_controller.clear()

    def card_batch_select(self, idx):
        return self.card_batch_controller.select(idx)

    def card_build_batch_panel(self):
        return build_batch_panel(self)


    def card_render_batch(self):
        return self.card_batch_controller.render()



    def card_import_batch_file(self):
        return self.card_batch_controller.import_file()



    def card_save_batch_project(self):
        return self.card_batch_controller.save_project()

    def card_load_batch_project(self):
        return self.card_batch_controller.load_project()


    def show_card_creator_page(self):
        return build_card_creator_page(self)

    def card_build_all_template_buttons(self):
        return build_all_template_buttons(self)

    def card_refresh_all_templates(self):
        return refresh_all_templates(self)

    def card_refresh_recent_templates(self):
        return refresh_recent_templates(self)

    def card_template(self):
        return self.card_creator_controller.current_template()


    def card_build_form(self):
        return build_card_form(self)


    def card_save_values(self):
        return self.card_data_controller.save_values()


    def card_values_plain(self):
        return self.card_data_controller.values_plain()





    def card_background_path(self):
        return self.card_render_service.resolve_background_path()


    def card_render_to_file(self, final=False, output_dir=None, output_path=None):
        return self.card_render_service.render_to_file(final, output_dir, output_path)


    def card_update_preview(self):
        return self.card_preview_controller.update()

    def card_render_final(self):
        return self.card_export_controller.render_final()



    def quick_cards_categories(self):
        try:
            data = text_library_engine.load_library()
            categories = sorted(data.keys())
            return categories or ["Chat"]
        except Exception:
            return ["Chat"]

    def show_quick_cards(self):
        self.set_active("Quick Cards")
        self.clear_main()
        self.page_title("Quick Cards")

        self.text_library_data = text_library_engine.load_library()

        outer = ctk.CTkFrame(self.main, fg_color=DARK)
        outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        outer.grid_columnconfigure(0, weight=2)
        outer.grid_columnconfigure(1, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        left = ctk.CTkScrollableFrame(outer, fg_color=PANEL, corner_radius=18)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_columnconfigure(0, weight=1)
        self.quick_cards_tree = left

        right = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right.grid_columnconfigure(0, weight=1)

        cats = sorted(self.text_library_data.keys()) or ["Chat"]
        if self.quick_cards_target_category.get() not in cats:
            self.quick_cards_target_category.set(cats[0])

        ctk.CTkLabel(right, text="Quick Card Manager", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

        ctk.CTkLabel(right, text="Target Category", text_color="#BCA870").grid(row=1, column=0, padx=18, pady=(8, 4), sticky="w")
        ctk.CTkOptionMenu(right, values=cats, variable=self.quick_cards_target_category, fg_color="#333333", button_color="#444444", button_hover_color="#555555").grid(row=2, column=0, padx=18, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(right, text="New Category", text_color="#BCA870").grid(row=3, column=0, padx=18, pady=(8, 4), sticky="w")
        ctk.CTkEntry(right, textvariable=self.text_library_new_category).grid(row=4, column=0, padx=18, pady=(0, 8), sticky="ew")
        ctk.CTkButton(right, text="+ ADD CATEGORY", fg_color="#333333", hover_color="#444444", command=self.quick_cards_add_category).grid(row=5, column=0, padx=18, pady=(0, 12), sticky="ew")

        ctk.CTkLabel(right, text="New Text", text_color="#BCA870").grid(row=6, column=0, padx=18, pady=(8, 4), sticky="w")
        ctk.CTkEntry(right, textvariable=self.text_library_new_text).grid(row=7, column=0, padx=18, pady=(0, 8), sticky="ew")

        ctk.CTkButton(right, text="+ SAVE TEXT", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=self.quick_cards_add_text).grid(row=8, column=0, padx=18, pady=(0, 8), sticky="ew")
        ctk.CTkButton(right, text="SAVE LIVE CARD TEXT", fg_color="#333333", hover_color="#444444", command=self.quick_cards_save_live_text).grid(row=9, column=0, padx=18, pady=(0, 8), sticky="ew")
        ctk.CTkButton(right, text="OPEN LIVE CARD", fg_color="#333333", hover_color="#444444", command=self.show_live_card).grid(row=10, column=0, padx=18, pady=(0, 18), sticky="ew")

        ctk.CTkLabel(
            right,
            text="Click a text on the left to send it straight to Live Card.\\nSAVE QUICK uses Target Category.",
            text_color="#777777",
            justify="left",
            wraplength=300
        ).grid(row=11, column=0, padx=18, pady=(8, 18), sticky="w")

        self.quick_cards_build_tree()



    def live_card_set_message_text(self, text):
        return self.live_card_controller.live_card_set_message_text(text)

    def live_card_get_message_text(self):
        return self.live_card_controller.live_card_get_message_text()

    def live_card_apply_pending_text(self):
        return self.live_card_controller.live_card_apply_pending_text()

    def quick_cards_build_tree(self):
        if not hasattr(self, "quick_cards_tree"):
            return

        for w in self.quick_cards_tree.winfo_children():
            w.destroy()

        row = 0
        for category in sorted(self.text_library_data.keys()):
            collapsed = category in self.quick_cards_collapsed
            header = ctk.CTkFrame(self.quick_cards_tree, fg_color="#111111", corner_radius=10)
            header.grid(row=row, column=0, padx=12, pady=(10, 4), sticky="ew")
            header.grid_columnconfigure(1, weight=1)

            arrow = "▶" if collapsed else "▼"
            ctk.CTkButton(header, text=arrow, width=42, fg_color="#333333", hover_color="#444444", command=lambda c=category: self.quick_cards_toggle_category(c)).grid(row=0, column=0, padx=(8, 4), pady=8)
            ctk.CTkLabel(header, text=category, text_color=GOLD, font=ctk.CTkFont(size=16, weight="bold")).grid(row=0, column=1, padx=4, pady=8, sticky="w")
            ctk.CTkButton(header, text="✎", width=42, fg_color="#333333", hover_color="#444444", command=lambda c=category: self.quick_cards_rename_category(c)).grid(row=0, column=2, padx=4, pady=8)
            ctk.CTkButton(header, text="DEL", width=54, fg_color="#5A1F1F", hover_color="#7A2A2A", command=lambda c=category: self.quick_cards_delete_category(c)).grid(row=0, column=3, padx=(4, 8), pady=8)
            row += 1

            if not collapsed:
                items = self.text_library_data.get(category, [])
                if not items:
                    ctk.CTkLabel(self.quick_cards_tree, text="No texts.", text_color="#777777").grid(row=row, column=0, padx=34, pady=4, sticky="w")
                    row += 1
                for text in items:
                    item = ctk.CTkFrame(self.quick_cards_tree, fg_color="#0B0B0B", corner_radius=8)
                    item.grid(row=row, column=0, padx=34, pady=3, sticky="ew")
                    item.grid_columnconfigure(0, weight=1)

                    editing = (
                        getattr(self, "quick_cards_editing_category", None) == category
                        and getattr(self, "quick_cards_editing_text", None) == text
                    )

                    if editing:
                        edit_entry = ctk.CTkEntry(item, textvariable=self.quick_cards_edit_text_var)
                        edit_entry.grid(row=0, column=0, padx=(8, 4), pady=6, sticky="ew")
                        edit_entry.focus_set()
                        edit_entry.select_range(0, "end")
                        edit_entry.bind("<Return>", lambda _e, c=category, t=text: self.quick_cards_commit_text_edit(c, t))
                        edit_entry.bind("<Escape>", lambda _e: self.quick_cards_cancel_text_edit())

                        ctk.CTkButton(
                            item,
                            text="SAVE",
                            width=60,
                            fg_color=GOLD,
                            text_color="#111111",
                            hover_color=GOLD_DARK,
                            command=lambda c=category, t=text: self.quick_cards_commit_text_edit(c, t)
                        ).grid(row=0, column=1, padx=4, pady=6)

                        ctk.CTkButton(
                            item,
                            text="CANCEL",
                            width=70,
                            fg_color="#333333",
                            hover_color="#444444",
                            command=self.quick_cards_cancel_text_edit
                        ).grid(row=0, column=2, padx=(4, 8), pady=6)

                    else:
                        ctk.CTkButton(
                            item,
                            text=text,
                            anchor="w",
                            fg_color="#171717",
                            hover_color="#2C2C2C",
                            text_color="#D9C58C",
                            command=lambda t=text: self.quick_cards_use_text(t)
                        ).grid(row=0, column=0, padx=(8, 4), pady=6, sticky="ew")

                        ctk.CTkButton(
                            item,
                            text="✎",
                            width=42,
                            fg_color="#333333",
                            hover_color="#444444",
                            command=lambda c=category, t=text: self.quick_cards_start_text_edit(c, t)
                        ).grid(row=0, column=1, padx=4, pady=6)

                        ctk.CTkButton(
                            item,
                            text="DEL",
                            width=48,
                            fg_color="#5A1F1F",
                            hover_color="#7A2A2A",
                            command=lambda c=category, t=text: self.quick_cards_delete_text(c, t)
                        ).grid(row=0, column=2, padx=(4, 8), pady=6)

                    row += 1

        self.quick_cards_tree.grid_columnconfigure(0, weight=1)


    def quick_cards_toggle_category(self, category):
        if category in self.quick_cards_collapsed:
            self.quick_cards_collapsed.remove(category)
        else:
            self.quick_cards_collapsed.add(category)
        self.show_quick_cards()

    def quick_cards_use_text(self, text):
        self.live_card_pending_text = str(text or "").strip()
        self.show_live_card()
        self.after(80, self.live_card_apply_pending_text)
        self.after(120, self.update_render_preview)

    def quick_cards_add_category(self):
        category = self.text_library_new_category.get().strip()
        if not category:
            messagebox.showinfo("Quick Cards", "Please enter a category name.")
            return
        self.text_library_data = text_library_engine.add_category(category)
        self.text_library_new_category.set("")
        self.quick_cards_target_category.set(category)
        if category in self.quick_cards_collapsed:
            self.quick_cards_collapsed.remove(category)
        self.show_quick_cards()

    def quick_cards_rename_category(self, category):
        new_name = simpledialog.askstring("Quick Cards", "New category name:", initialvalue=category)
        if not new_name:
            return
        new_name = new_name.strip()
        if not new_name:
            return
        self.text_library_data = text_library_engine.rename_category(category, new_name)
        self.quick_cards_target_category.set(new_name)
        self.show_quick_cards()

    def quick_cards_delete_category(self, category):
        if not messagebox.askyesno("Quick Cards", f"Delete category '{category}'?\\nAll texts inside will be removed."):
            return
        self.text_library_data = text_library_engine.delete_category(category)
        self.show_quick_cards()

    def quick_cards_add_text(self):
        text = self.text_library_new_text.get().strip()
        if not text:
            messagebox.showinfo("Quick Cards", "Please enter a text first.")
            return
        category = self.quick_cards_target_category.get()
        self.text_library_data = text_library_engine.add_text(category, text)
        self.text_library_new_text.set("")
        self.live_card_pending_text = text
        self.show_quick_cards()

    def quick_cards_save_live_text(self):
        text = self.live_card_get_message_text()
        if not text:
            messagebox.showinfo("Quick Cards", "No Live Card text found.")
            return
        categories = self.quick_cards_categories()
        if self.quick_cards_target_category.get() not in categories:
            self.quick_cards_target_category.set("Chat" if "Chat" in categories else categories[0])
        category = self.quick_cards_target_category.get()
        self.text_library_data = text_library_engine.add_text(category, text)
        messagebox.showinfo("Quick Cards", f"Text saved.\nCategory: {category}")
        self.show_quick_cards()



    def quick_cards_start_text_edit(self, category, text):
        self.quick_cards_editing_category = category
        self.quick_cards_editing_text = text
        self.quick_cards_edit_text_var.set(text)
        self.show_quick_cards()

    def quick_cards_commit_text_edit(self, category, text):
        new_text = self.quick_cards_edit_text_var.get().strip()
        if not new_text:
            messagebox.showinfo("Quick Cards", "Text cannot be empty.")
            return
        self.text_library_data = text_library_engine.edit_text(category, text, new_text)
        self.quick_cards_editing_category = None
        self.quick_cards_editing_text = None
        self.quick_cards_edit_text_var.set("")
        self.show_quick_cards()

    def quick_cards_cancel_text_edit(self):
        self.quick_cards_editing_category = None
        self.quick_cards_editing_text = None
        self.quick_cards_edit_text_var.set("")
        self.show_quick_cards()

    def quick_cards_delete_text(self, category, text):
        if not messagebox.askyesno("Quick Cards", "Delete this text?"):
            return
        self.text_library_data = text_library_engine.delete_text(category, text)
        self.show_quick_cards()


    def show_obs_page(self):
        self.set_active("OBS Connection")
        self.clear_main()
        self.page_title("OBS Connection")
        box = ctk.CTkFrame(self.main, fg_color=PANEL, corner_radius=18)
        box.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        rows = [
            ("Host", self.host, False),
            ("Port", self.port, False),
            ("Password", self.password, True),
            ("Scene optional", self.scene_name, False),
            ("Caption Group", self.caption_group, False),
            ("Text Source", self.caption_text, False),
            ("Caption Banner Source", self.caption_banner_source, False),
            ("Caption Render Source", self.caption_render_source, False),
            ("Scene Card Source", self.scene_card_source, False),
        ]
        for label, var, hidden in rows:
            row = ctk.CTkFrame(box, fg_color="transparent")
            row.pack(fill="x", padx=24, pady=8)
            ctk.CTkLabel(row, text=label, width=190, anchor="w", text_color="#BCA870").pack(side="left")
            ctk.CTkEntry(row, textvariable=var, show="*" if hidden else None).pack(side="left", fill="x", expand=True)
        btnrow = ctk.CTkFrame(box, fg_color="transparent")
        btnrow.pack(fill="x", padx=24, pady=18)
        ctk.CTkButton(btnrow, text="CONNECT", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=self.connect_obs).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btnrow, text="SAVE SETTINGS", fg_color="#333333", command=self.save_config).pack(side="left", padx=8)



    def obs_workflow_set_sidebar_status(self, connected):
        return self.obs_workflow_controller.obs_workflow_set_sidebar_status(connected)

    def obs_workflow_log(self, message):
        return self.obs_workflow_controller.obs_workflow_log(message)

    def obs_workflow_mark_command(self, message):
        return self.obs_workflow_controller.obs_workflow_mark_command(message)

    def obs_workflow_is_connected(self):
        return self.obs_workflow_controller.obs_workflow_is_connected()

    def obs_workflow_connect(self):
        return self.obs_workflow_controller.obs_workflow_connect()

    def obs_workflow_disconnect(self):
        return self.obs_workflow_controller.obs_workflow_disconnect()

    def obs_workflow_refresh(self, silent=False):
        return self.obs_workflow_controller.obs_workflow_refresh(silent)

    def obs_workflow_banner_action(self, action, text=""):
        return self.obs_workflow_controller.obs_workflow_banner_action(action, text)

    def obs_workflow_current_live_text(self):
        return self.obs_workflow_controller.obs_workflow_current_live_text()

    def obs_workflow_load_scene_favorites(self):
        return self.obs_workflow_controller.obs_workflow_load_scene_favorites()

    def obs_workflow_add_scene_favorite(self, scene_name):
        return self.obs_workflow_controller.obs_workflow_add_scene_favorite(scene_name)

    def obs_workflow_remove_scene_favorite(self, scene_name):
        return self.obs_workflow_controller.obs_workflow_remove_scene_favorite(scene_name)

    def obs_workflow_update_scene_ui(self):
        return self.obs_workflow_controller.obs_workflow_update_scene_ui()

    def obs_workflow_switch_scene(self, scene_name):
        return self.obs_workflow_controller.obs_workflow_switch_scene(scene_name)

    def obs_workflow_refresh_sources_only(self):
        return self.obs_workflow_controller.obs_workflow_refresh_sources_only()

    def obs_workflow_update_source_row_ui(self, source_name, enabled):
        return self.obs_workflow_controller.obs_workflow_update_source_row_ui(source_name, enabled)

    def obs_workflow_set_source_visibility(self, source_name, enabled):
        return self.obs_workflow_controller.obs_workflow_set_source_visibility(source_name, enabled)

    def obs_workflow_required_overlay_sources(self):
        return self.obs_workflow_controller.obs_workflow_required_overlay_sources()

    def obs_workflow_normalize_source_name(self, name):
        return self.obs_workflow_controller.obs_workflow_normalize_source_name(name)

    def obs_workflow_source_matches(self, required_name, found_names):
        return self.obs_workflow_controller.obs_workflow_source_matches(required_name, found_names)

    def obs_workflow_scan_overlay_health(self, silent=False):
        return self.obs_workflow_controller.obs_workflow_scan_overlay_health(silent)

    def obs_workflow_health_counts(self):
        return self.obs_workflow_controller.obs_workflow_health_counts()

    def obs_workflow_current_scene_health(self):
        return self.obs_workflow_controller.obs_workflow_current_scene_health()

    def obs_workflow_recent_activity(self):
        return self.obs_workflow_controller.obs_workflow_recent_activity()

    def obs_workflow_format_activity(self, text):
        return self.obs_workflow_controller.obs_workflow_format_activity(text)

    def obs_workflow_overlay_installer_source_values(self):
        return self.obs_workflow_controller.obs_workflow_overlay_installer_source_values()

    def obs_workflow_overlay_installer_set_source(self, scene_name):
        return self.obs_workflow_controller.obs_workflow_overlay_installer_set_source(scene_name)

    def obs_workflow_overlay_installer_toggle_scene(self, scene_name):
        return self.obs_workflow_controller.obs_workflow_overlay_installer_toggle_scene(scene_name)

    def obs_workflow_overlay_installer_select_missing(self):
        return self.obs_workflow_controller.obs_workflow_overlay_installer_select_missing()

    def obs_workflow_overlay_installer_clear_selection(self):
        return self.obs_workflow_controller.obs_workflow_overlay_installer_clear_selection()

    def obs_workflow_overlay_installer_install_selected(self):
        return self.obs_workflow_controller.obs_workflow_overlay_installer_install_selected()


    def silent_director_reload(self):
        return director_management.reload_presets(self)

    def silent_director_get_selected_preset(self):
        return director_management.get_selected_preset(self)

    def silent_director_create_preset(self):
        return director_management.create_preset(self)

    def silent_director_duplicate_preset(self, preset=None):
        return director_management.duplicate_preset(self, preset)

    def silent_director_delete_selected(self):
        return director_management.delete_selected_preset(self)


    def director_set_active_action(self, index=None):
        return director_support.director_set_active_action(self, index)

    def director_clear_active_action(self):
        self.director_set_active_action(None)

    def director_log_add(self, message):
        return director_support.director_log_add(self, message)

    def director_set_status(self, status, current="-", progress=""):
        return director_support.director_set_status(self, status,current,progress)

    def director_request_stop(self):
        return director_support.director_request_stop(self)

    def director_action_label(self, action):
        return director_support.director_action_label(self, action)



    def silent_director_show_banner_direct(self, text):
        return director_support.silent_director_show_banner_direct(self, text)

    def silent_director_run_preset(self, preset=None):
        return run_silent_director_preset(self, preset)


    def silent_director_scene_values(self):
        return director_support.silent_director_scene_values(self)

    def silent_director_load_editor(self, preset):
        return director_management.load_editor(self, preset)

    def silent_director_save_selected(self):
        return director_management.save_selected_preset(self)


    def silent_director_source_values(self):
        return director_support.silent_director_source_values(self)

    def silent_director_normalize_wait_seconds(self):
        return director_support.silent_director_normalize_wait_seconds(self)

    def silent_director_update_action_fields(self, *_args):
        return director_support.silent_director_update_action_fields(self)

    def silent_director_cancel_action_edit(self):
        return director_management.cancel_action_edit(self)

    def silent_director_edit_action(self, index):
        return director_management.edit_action(self, index)

    def silent_director_duplicate_action(self, index):
        return director_management.duplicate_action(self, index)

    def silent_director_move_action(self, index, direction):
        return director_management.move_action(self, index, direction)

    def silent_director_drag_start(self, event, index):
        return start_silent_director_drag(self, event, index)


    def silent_director_drag_target_from_y(self, y_root):
        return silent_director_drag_target(self, y_root)


    def silent_director_show_floating_drop_indicator(self, target_index):
        return show_silent_director_drop_indicator(self, target_index)


    def silent_director_hide_floating_drop_indicator(self):
        return hide_silent_director_drop_indicator(self)


    def silent_director_drag_motion(self, event):
        return move_silent_director_drag(self, event)


    def silent_director_drag_release(self, event=None):
        return release_silent_director_drag(self, event)


    def silent_director_drag_cancel(self):
        return cancel_silent_director_drag(self)


    def silent_director_timeline_style(self, action_type):
        return director_support.silent_director_timeline_style(self, action_type)

    def silent_director_timeline_detail(self, action):
        return director_support.silent_director_timeline_detail(self, action)

    def silent_director_render_actions_list(self):
        return render_actions_list(self)






    def silent_director_add_action(self):
        return director_management.add_action(self)


    def silent_director_delete_action(self, index):
        return director_management.delete_action(self, index)

    def silent_director_preset_stats(self, preset):
        return director_support.silent_director_preset_stats(self, preset)

    def silent_director_format_duration(self, total_seconds):
        return director_support.silent_director_format_duration(self, total_seconds)

    def silent_director_preset_stats_text(self, preset):
        return director_support.silent_director_preset_stats_text(self, preset)

    def silent_director_toggle_favorite(self, preset):
        return director_support.silent_director_toggle_favorite(self, preset)

    def silent_director_toggle_favorites_filter(self):
        return director_support.silent_director_toggle_favorites_filter(self)

    def silent_director_preset_icon(self, preset):
        return director_support.silent_director_preset_icon(self, preset)

    def silent_director_icon_options(self):
        return director_support.silent_director_icon_options(self)

    def silent_director_filtered_presets(self):
        return director_support.silent_director_filtered_presets(self)

    def silent_director_clear_search(self):
        return director_support.silent_director_clear_search(self)

    def silent_director_render_filtered_presets(self, *_args):
        return render_filtered_presets(self, *_args)

    def show_silent_director_page(self):
        return build_silent_director_page(self)


    def show_obs_workflow_page(self):
        return self.obs_workflow_controller.show_obs_workflow_page()


    def voice_script_path(self):
        return (
            Path(__file__).resolve().parent
            / "tools"
            / "voice_listener.ps1"
        )

    def normalize_voice_text(self, value):
        return " ".join(str(value or "").strip().casefold().split())

    def voice_trigger_matches(self, heard):
        phrase = self.normalize_voice_text(self.voice_trigger_phrase.get())
        heard = self.normalize_voice_text(heard)
        return bool(phrase and heard and (phrase == heard or phrase in heard))

    def voice_reader_loop(self, process):
        try:
            while not self.voice_stop_requested:
                line = process.stdout.readline()
                if line == "":
                    break

                line = line.strip()
                if not line:
                    continue

                if line == "__READY__":
                    self.after(0, lambda: self.voice_status_var.set("LISTENING"))
                    continue

                if line.startswith("__WARN__|"):
                    warning = line.split("|", 1)[1]
                    self.after(0, lambda text=warning: self.voice_status_var.set(f"LISTENING · {text}"))
                    continue

                if line.startswith("__ERROR__|"):
                    error = line.split("|", 1)[1]
                    self.after(0, lambda text=error: self.voice_status_var.set(f"ERROR: {text[:70]}"))
                    continue

                if line.startswith("__HEARD__|"):
                    heard = line.split("|", 1)[1].strip()
                    self.after(0, lambda text=heard: self.voice_last_heard_var.set(text))

                    if self.voice_trigger_matches(heard):
                        self.after(0, lambda: self.voice_status_var.set("COMMAND DETECTED"))
                        self.after(0, self.open_quick_caption)
                        self.after(800, lambda: self.voice_status_var.set("LISTENING"))
        except Exception as exc:
            if not self.voice_stop_requested:
                self.after(0, lambda text=str(exc): self.voice_status_var.set(f"ERROR: {text[:70]}"))
        finally:
            if not self.voice_stop_requested and self.voice_status_var.get() != "ERROR":
                self.after(0, lambda: self.voice_status_var.set("STOPPED"))

    def start_voice_trigger(self):
        if sys.platform != "win32":
            self.voice_status_var.set("WINDOWS ONLY")
            return

        if self.voice_process is not None:
            try:
                if self.voice_process.poll() is None:
                    self.voice_status_var.set("LISTENING")
                    return
            except Exception:
                pass

        script = self.voice_script_path()
        if not script.exists():
            self.voice_status_var.set("ERROR: voice_listener.ps1 missing")
            return

        self.voice_stop_requested = False
        self.voice_status_var.set("STARTING...")

        command = [
            "powershell.exe",
            "-NoProfile",
            "-ExecutionPolicy", "Bypass",
            "-File", str(script),
            "-Culture", self.voice_culture.get().strip(),
        ]

        try:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW

            self.voice_process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                bufsize=1,
                startupinfo=startupinfo,
                creationflags=subprocess.CREATE_NO_WINDOW,
            )

            self.voice_reader_thread = threading.Thread(
                target=self.voice_reader_loop,
                args=(self.voice_process,),
                daemon=True,
            )
            self.voice_reader_thread.start()
        except Exception as exc:
            self.voice_process = None
            self.voice_status_var.set(f"ERROR: {str(exc)[:70]}")

    def stop_voice_trigger(self):
        self.voice_stop_requested = True
        process = self.voice_process
        self.voice_process = None

        if process is not None:
            try:
                process.terminate()
                process.wait(timeout=1.2)
            except Exception:
                try:
                    process.kill()
                except Exception:
                    pass

        self.voice_status_var.set("OFF")

    def restart_voice_trigger(self):
        self.stop_voice_trigger()
        if self.voice_enabled.get():
            self.after(250, self.start_voice_trigger)

    def toggle_voice_trigger(self):
        self.save_config()
        if self.voice_enabled.get():
            self.start_voice_trigger()
        else:
            self.stop_voice_trigger()

    def test_voice_trigger(self):
        self.voice_last_heard_var.set("Manual F8 test")
        self.open_quick_caption()

    def on_app_close(self):
        self.stop_voice_trigger()
        self.destroy()

    def show_settings_page(self):
        return self.settings_controller.show_settings_page()

    def browse_project_folder(self):
        return self.settings_controller.browse_project_folder()

    def browse_card_output_folder(self):
        return self.settings_controller.browse_card_output_folder()

    def browse_card_batch_output_folder(self):
        return self.settings_controller.browse_card_batch_output_folder()

    def open_card_output_folder(self):
        return self.settings_controller.open_card_output_folder()

    def open_card_batch_output_folder(self):
        return self.settings_controller.open_card_batch_output_folder()

    def update_preview(self):
        if hasattr(self, "message_box"):
            self.update_render_preview()

    def open_quick_caption(self):
        return self.live_card_controller.open_quick_caption()


    def ensure_obs_ready(self):
        try:
            connected = self.obs_workflow_is_connected() if hasattr(self, "obs_workflow_is_connected") else self.obs.is_connected()
            if hasattr(self, "obs_workflow_state"):
                if hasattr(self.obs_workflow_state, "set_connected"):
                    self.obs_workflow_state.set_connected(connected)
                else:
                    self.obs_workflow_state.connected = connected
            if hasattr(self, "obs_workflow_set_sidebar_status"):
                self.obs_workflow_set_sidebar_status(connected)

            if not connected:
                messagebox.showinfo("OBS", "OBS ist nicht verbunden.")
                return False
            return True
        except Exception:
            try:
                self.obs_workflow_set_sidebar_status(False)
            except Exception:
                pass
            try:
                if hasattr(self.obs_workflow_state, "set_connected"):
                    self.obs_workflow_state.set_connected(False)
                else:
                    self.obs_workflow_state.connected = False
            except Exception:
                pass
            messagebox.showinfo("OBS", "OBS ist nicht verbunden.")
            return False


    def connect_obs(self):
        try:
            self.obs.connect(self.host.get().strip(), self.port.get().strip(), self.password.get())
            self.obs_workflow_set_sidebar_status(True) if hasattr(self, "obs_workflow_set_sidebar_status") else self.status_label.configure(text="● Connected", text_color="#6EE08C")
            self.save_config()
            messagebox.showinfo("OBS", "Verbindung erfolgreich.")
        except Exception as e:
            self.obs_workflow_set_sidebar_status(False) if hasattr(self, "obs_workflow_set_sidebar_status") else self.status_label.configure(text="● Not connected", text_color="#D86A6A")
            messagebox.showerror("OBS Verbindung fehlgeschlagen", str(e))

    def save_config(self):
        return self.settings_controller.save_config()

    def current_scene(self):
        return self.obs.current_scene(self.scene_name.get().strip())


    def get_current_banner_profile(self):
        selected_banner_path = self.config_data.get("selected_banner_path", "")
        if not selected_banner_path:
            return None
        try:
            from pathlib import Path
            selected = Path(selected_banner_path)
            project = Path(self.project_folder.get())
            key = str(selected.relative_to(project))
            return self.banner_profiles.get(key)
        except Exception:
            return None


    def render_smart_caption(self, text, profiler=None):
        self.last_render_path = EXPORT_DIR / "caption_render.png"
        profile = self.get_current_banner_profile() or {}
        render_caption_png(
            text=text,
            output_path=self.last_render_path,
            width=int(self.caption_render_width.get()),
            height=int(self.caption_render_height.get()),
            font_family=profile.get("font_family", self.caption_font_family.get()),
            font_size=int(profile.get("font_size", self.caption_font_size.get())),
            text_color=profile.get("text_color", self.caption_text_color.get()),
            stroke_color=profile.get("stroke_color", self.caption_stroke_color.get()),
            stroke_width=int(profile.get("stroke_width", self.caption_stroke_width.get())),
            uppercase=bool(profile.get("uppercase", self.caption_uppercase.get())),
            banner_path=self.config_data.get("selected_banner_path", ""),
            text_area=profile.get("text_area"),
            safe_left=int(self.caption_safe_left.get()),
            safe_right=int(self.caption_safe_right.get()),
            safe_top=int(self.caption_safe_top.get()),
            safe_bottom=int(self.caption_safe_bottom.get()),
            profiler=profiler,
            png_compress_level=self.config_data.get("caption_png_compress_level", 1),
        )
        return self.last_render_path


    def update_render_preview(self):
        if not hasattr(self, "preview_frame") or not hasattr(self, "message_box"):
            return

        for w in self.preview_frame.winfo_children():
            w.destroy()

        text = self.message_box.get("1.0", "end").strip() or "..."
        try:
            preview_path = self.render_smart_caption(text)

            from PIL import Image
            img = Image.open(preview_path).convert("RGBA")
            img.thumbnail((520, 300))

            self.live_preview_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            ctk.CTkLabel(self.preview_frame, image=self.live_preview_image, text="").place(relx=0.5, rely=0.5, anchor="center")

            if hasattr(self, "render_status_label"):
                banner_name = self.live_card_current_banner_name()
                self.render_status_label.configure(
                    text=(
                        f"🟢 Preview ready\n"
                        f"Engine: {self.caption_engine.get()}\n"
                        f"Banner: {banner_name}"
                    ),
                    text_color="#8FE6A0"
                )
                if hasattr(self, "live_card_banner_name_label"):
                    self.live_card_banner_name_label.configure(
                        text=banner_name
                    )
        except Exception as e:
            ctk.CTkLabel(
                self.preview_frame,
                text=f"Preview konnte nicht gerendert werden:\n{e}",
                text_color="#D86A6A",
                wraplength=360,
                justify="center"
            ).place(relx=0.5, rely=0.5, anchor="center")
            if hasattr(self, "render_status_label"):
                self.render_status_label.configure(text="🔴 Preview error", text_color="#D86A6A")


    def play_selected_sound_effect_for_show(self, profiler=None):
        """Restart the configured OBS Media Source for SHOW.

        PREVIEW intentionally remains local through SoundService. Automatic
        SHOW playback is best-effort so an audio-source problem never cancels
        the Live Card itself.
        """
        if not bool(self.config_data.get("stream_effect_enabled", False)):
            if profiler is not None:
                profiler.mark("Sound skipped: automatic playback disabled")
            return None

        relative = str(
            self.config_data.get("selected_sound_effect", "") or ""
        ).strip()
        if not relative:
            if profiler is not None:
                profiler.mark("Sound skipped: no effect selected")
            return None

        source_name = self.stream_effect_source.get().strip()
        if not source_name:
            LOGGER.warning("No OBS Stream Effect Media Source is configured.")
            if profiler is not None:
                profiler.mark("Sound failed: no OBS Media Source configured")
            return False

        try:
            service = self._sync_sound_service_project()
            media_file = service.resolve(relative)
            if media_file is None or not service.exists(relative):
                LOGGER.warning(
                    "Configured Stream Effect is unavailable: %s",
                    relative,
                )
                if profiler is not None:
                    profiler.mark("Sound failed: WAV unavailable")
                return False

            if profiler is not None:
                profiler.mark("OBS media playback requested")
            self.obs.play_media_file(source_name, media_file)
            if profiler is not None:
                profiler.mark("OBS media playback request finished")
            return True
        except Exception:
            if profiler is not None:
                profiler.mark("OBS media playback request failed")
            LOGGER.exception(
                "OBS Stream Effect playback failed for %s via source %s",
                relative,
                source_name,
            )
            return False


    def show_card(self):
        profiler = SyncProfiler(
            enabled=bool(self.config_data.get("sync_profiler_enabled", False)),
            session_name="LiveCard SHOW",
        )
        profiler.mark("SHOW event received")

        if not self.ensure_obs_ready():
            profiler.mark("SHOW aborted: OBS not ready")
            profiler.save()
            return

        text = self.message_box.get("1.0", "end").strip() if hasattr(self, "message_box") else ""
        if not text:
            text = "..."

        try:
            scene = self.current_scene()
            profiler.mark("OBS scene resolved")

            selected_banner_path = self.config_data.get("selected_banner_path", "")

            if self.caption_engine.get() == "smart_png":
                try:
                    profiler.mark("Smart caption render requested")
                    png = self.render_smart_caption(text, profiler=profiler)
                    profiler.mark("Smart caption render finished")
                    self.obs.set_image_file(self.caption_render_source.get().strip(), png)
                    profiler.mark("OBS caption image update finished")
                except Exception:
                    profiler.mark("SHOW failed: caption render source")
                    messagebox.showerror("Caption Render Source nicht gefunden", f"Die OBS-Bildquelle '{self.caption_render_source.get().strip()}' wurde nicht gefunden.\n\nBitte OBS Connection prüfen.")
                    return

                try:
                    self.obs.enable_source(scene, self.caption_text.get().strip(), False)
                except Exception:
                    pass
                try:
                    self.obs.enable_source(scene, self.caption_render_source.get().strip(), True)
                except Exception:
                    pass
            else:
                if selected_banner_path:
                    try:
                        self.obs.set_image_file(self.caption_banner_source.get().strip(), selected_banner_path)
                        profiler.mark("OBS banner image update finished")
                    except Exception:
                        profiler.mark("SHOW failed: caption banner source")
                        messagebox.showerror("Caption Banner Source nicht gefunden", f"Die OBS-Bildquelle '{self.caption_banner_source.get().strip()}' wurde nicht gefunden.\n\nBitte OBS Connection prüfen.")
                        return
                try:
                    self.obs.set_text(self.caption_text.get().strip(), text)
                    profiler.mark("OBS caption text update finished")
                except Exception:
                    profiler.mark("SHOW failed: text source")
                    messagebox.showerror("Text Source nicht gefunden", f"Die OBS-Textquelle '{self.caption_text.get().strip()}' wurde nicht gefunden.\n\nBitte OBS Connection prüfen.")
                    return

                try:
                    self.obs.enable_source(scene, self.caption_render_source.get().strip(), False)
                except Exception:
                    pass
                try:
                    self.obs.enable_source(scene, self.caption_text.get().strip(), True)
                except Exception:
                    pass

            profiler.mark("Banner group enable requested")
            self.obs.enable_source(scene, self.caption_group.get().strip(), True)
            profiler.mark("Banner group enable request finished")

            if self.hide_timer:
                self.hide_timer.cancel()
            seconds = max(1, int(self.duration.get()))
            self.hide_timer = threading.Timer(seconds, lambda: self.after(0, self.hide_card))
            self.hide_timer.daemon = True
            self.hide_timer.start()
            profiler.mark("Hide timer started")
            self.save_config()
            profiler.mark("Config save finished")

            self.play_selected_sound_effect_for_show(profiler=profiler)
            profiler.mark("SHOW completed")
        except Exception as e:
            profiler.mark(f"SHOW exception: {type(e).__name__}")
            messagebox.showerror("SHOW fehlgeschlagen", str(e))
        finally:
            profiler.save()

        try:
            self.obs_workflow_banner_action("SHOW Live Card", self.obs_workflow_current_live_text())
        except Exception:
            pass


    def hide_card(self):
        if not self.ensure_obs_ready(): return
        try: self.obs.enable_source(self.current_scene(), self.caption_group.get().strip(), False)
        except Exception: pass
        try:
            self.obs_workflow_banner_action("HIDE Live Card")
        except Exception:
            pass


    def enter_to_show(self, event):
        if event.state & 0x0001:
            return None
        self.show_card()
        return "break"

    def clear_text(self):
        if hasattr(self, "message_box"):
            self.message_box.delete("1.0", "end")
            self.message_box.focus_set()
            self.update_preview()
        try:
            from .voice_control.live_card_voice import reset_live_card_translation
            reset_live_card_translation(self)
        except Exception:
            pass
        try:
            self.obs_workflow_banner_action("CLEAR Live Card")
        except Exception:
            pass


    def save_current_quick(self):
        text = self.live_card_get_message_text() if hasattr(self, "live_card_get_message_text") else ""
        if not text and hasattr(self, "message_box"):
            try:
                text = self.message_box.get("1.0", "end").strip()
            except Exception:
                text = ""
        if not text:
            messagebox.showinfo("Quick Cards", "No Live Card text found.")
            return

        categories = self.quick_cards_categories() if hasattr(self, "quick_cards_categories") else ["Chat"]
        if not hasattr(self, "quick_cards_target_category") or self.quick_cards_target_category.get() not in categories:
            self.quick_cards_target_category = ctk.StringVar(value="Chat" if "Chat" in categories else categories[0])

        category = self.quick_cards_target_category.get()
        text_library_engine.add_text(category, text)
        self.live_card_pending_text = text
        messagebox.showinfo("Quick Cards", f"Text saved.\nCategory: {category}")


    def set_message(self, text):
        if not hasattr(self, "message_box"): return
        self.message_box.delete("1.0", "end")
        self.message_box.insert("1.0", text)
        self.update_preview()

    def use_favorite(self, text):
        self.show_live_card()
        self.set_message(text)

def main():
    app = VadafokStudio()
    app.mainloop()
