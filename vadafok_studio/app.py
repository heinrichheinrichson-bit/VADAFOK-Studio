
import os
import tkinter as tk
from tkinter import filedialog
import threading
import customtkinter as ctk
from tkinter import messagebox, simpledialog, filedialog, simpledialog
from PIL import Image

from .core.config import TEMPLATE_PROFILES_PATH, load_config, save_config, load_favorites, save_favorites, load_asset_meta, save_asset_meta, EXPORT_DIR, load_json, save_json, CARD_VALUES_PATH
from .core.library import scan_library, ROOT_FOLDERS, guessed_tags
from .core.obs_controller import OBSController
from .core.caption_renderer import render_caption_png
from .core.template_store import list_templates, load_template, save_template, create_template, set_background_from_file, background_path, import_legacy_templates, delete_template, duplicate_template, rename_template, set_default_template, get_default_template, ensure_background_file, template_dir
from .core.image_view import load_rgba, fit_image_to_box, pil_to_tk_photo_data, image_status
from .core.layout_engine import banner_profile_to_layout_field, apply_layout_field_to_banner_profile, create_default_template, render_template_card
from .core import style_engine
from .core import export_engine
from .core import batch_engine
from .core import text_library_engine
from .core import obs_workflow
from .core import scene_favorites
from .core.banner_profiles import load_banner_profiles, save_banner_profiles, ensure_profile, has_profile, profile_count, reset_profile_style

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
        self.wm_title("VADAFOK Studio 2.11.2")
        self.geometry("1360x840")
        self.minsize(1160, 740)

        self.config_data = load_config()
        self.favorites = load_favorites()
        self.asset_meta = load_asset_meta()
        self.banner_profiles = load_banner_profiles()
        self.template_profiles = load_json(TEMPLATE_PROFILES_PATH, {})
        self.template_store_migrated = import_legacy_templates(self.template_profiles)
        self.template_selected_name = "Default Stream Plan"
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
        self.card_creator_values = {}
        self.card_saved_values = load_json(CARD_VALUES_PATH, {})
        self.card_creator_preview_image = None
        self.card_creator_last_render = None
        self.card_output_name = ctk.StringVar(value="")
        self.card_auto_preview = ctk.BooleanVar(value=True)
        self.card_export_profile = ctk.StringVar(value="Broadcast PNG")
        self.card_batch_items = []
        self.card_batch_selected_index = None
        self.card_data_undo_stack = []
        self.card_data_redo_stack = []
        self.card_history_limit = 50
        self.obs = OBSController()
        self.obs_workflow_state = obs_workflow.OBSWorkflowState()
        self.scene_favorites = scene_favorites.load_favorites()
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
        self.last_render_path = EXPORT_DIR / "caption_render.png"
        self.text_library_new_text = ctk.StringVar(value="")
        self.text_library_new_category = ctk.StringVar(value="")
        self.quick_cards_collapsed = set()
        self.live_card_pending_text = ""
        self.quick_cards_target_category = ctk.StringVar(value="Chat")
        self.quick_cards_editing_category = None
        self.quick_cards_editing_text = None
        self.quick_cards_edit_text_var = ctk.StringVar(value="")

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
        self.library_section = ctk.StringVar(value="All")
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

    def build_sidebar(self):
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#050505")
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_propagate(False)
        ctk.CTkLabel(self.sidebar, text="🎭 VADAFOK", font=ctk.CTkFont(size=26, weight="bold"), text_color=GOLD).pack(anchor="w", padx=18, pady=(24, 0))
        ctk.CTkLabel(self.sidebar, text="Studio 2.11.2", text_color="#BCA870").pack(anchor="w", padx=20, pady=(0, 22))
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
        if hasattr(self, "main"):
            self.main.destroy()
        self.main = ctk.CTkFrame(self, fg_color=DARK, corner_radius=0)
        self.main.grid(row=0, column=1, sticky="nsew")
        self.main.grid_columnconfigure(0, weight=1)
        self.main.grid_rowconfigure(1, weight=1)

    def page_title(self, text):
        ctk.CTkLabel(self.main, text=text, font=ctk.CTkFont(size=28, weight="bold"), text_color=GOLD).grid(row=0, column=0, padx=28, pady=(24, 12), sticky="w")

    def show_library(self):
        self.set_active("Library")
        self.clear_main()
        self.page_title("Library")
        outer = ctk.CTkFrame(self.main, fg_color=DARK)
        outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        outer.grid_columnconfigure(0, weight=3)
        outer.grid_columnconfigure(1, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(left, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))
        top.grid_columnconfigure(3, weight=1)
        ctk.CTkLabel(top, text="Section", text_color="#BCA870").grid(row=0, column=0, padx=(0, 8))
        ctk.CTkOptionMenu(top, values=["All"] + ROOT_FOLDERS, variable=self.library_section, fg_color="#1A1A1A", button_color=GOLD_DARK, command=lambda _: self.render_library_grid()).grid(row=0, column=1, sticky="w")
        ctk.CTkCheckBox(top, text="Favorites", variable=self.favorite_filter, text_color="#BCA870", command=self.render_library_grid).grid(row=0, column=2, padx=(18, 8))
        entry = ctk.CTkEntry(top, textvariable=self.search_text, placeholder_text="Suche nach Datei, Kategorie oder Tag...")
        entry.grid(row=0, column=3, sticky="ew")
        entry.bind("<KeyRelease>", lambda e: self.render_library_grid())
        ctk.CTkButton(top, text="REFRESH", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=self.reload_library).grid(row=0, column=4, padx=(12, 0))

        self.library_info = ctk.CTkLabel(left, text="", text_color="#D9C58C", anchor="w", justify="left")
        self.library_info.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 8))
        self.library_grid = ctk.CTkScrollableFrame(left, fg_color="#0B0B0B", corner_radius=12)
        self.library_grid.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))

        right = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(right, text="Selection", font=ctk.CTkFont(size=18, weight="bold"), text_color=GOLD).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")
        self.selection_preview = ctk.CTkFrame(right, fg_color="#050505", corner_radius=12, border_color="#3A2A0D", border_width=1)
        self.selection_preview.grid(row=1, column=0, padx=18, pady=8, sticky="nsew")
        self.selection_name = ctk.CTkLabel(right, text="Noch nichts ausgewählt", text_color=TEXT, wraplength=300, justify="left")
        self.selection_name.grid(row=2, column=0, padx=18, pady=(8, 4), sticky="w")
        self.selection_meta = ctk.CTkLabel(right, text="", text_color="#BCA870", wraplength=300, justify="left")
        self.selection_meta.grid(row=3, column=0, padx=18, pady=(0, 12), sticky="w")
        ctk.CTkLabel(right, text="Actions", font=ctk.CTkFont(size=16, weight="bold"), text_color=GOLD).grid(row=4, column=0, padx=18, pady=(6, 4), sticky="w")
        actions = [
            ("SHOW / USE", self.default_selected_action, GOLD),
            ("USE AS CAPTION BANNER", self.use_selected_as_caption_banner, "#4A3913"),
            ("SHOW AS SCENE CARD", self.show_selected_scene_card, "#333333"),
            ("TOGGLE FAVORITE ⭐", self.toggle_selected_favorite, "#333333"),
            ("EDIT TAGS", self.edit_selected_tags, "#333333"),
            ("OPEN FOLDER", self.open_selected_folder, "#222222"),
            ("COPY PATH", self.copy_selected_path, "#222222"),
        ]
        for i, (text, cmd, color) in enumerate(actions, start=5):
            ctk.CTkButton(right, text=text, fg_color=color, text_color="#111111" if color == GOLD else TEXT, hover_color=GOLD_DARK if color in [GOLD, "#4A3913"] else "#444444", command=cmd).grid(row=i, column=0, padx=18, pady=4, sticky="ew")

        self.reload_library()

    def reload_library(self):
        self.library_items = scan_library(self.project_folder.get())
        self.render_library_grid()

    def item_key(self, item): return item.relative
    def item_is_favorite(self, item): return self.item_key(item) in self.asset_meta.get("favorites", [])
    def item_tags(self, item):
        stored = self.asset_meta.get("tags", {}).get(self.item_key(item), [])
        return list(dict.fromkeys(stored + guessed_tags(item)))

    def render_library_grid(self):
        if not hasattr(self, "library_grid"): return
        for w in self.library_grid.winfo_children(): w.destroy()
        self.thumbnail_refs = []
        section = self.library_section.get()
        query = self.search_text.get().strip().lower()
        items = self.library_items
        if section != "All": items = [i for i in items if i.section == section]
        if self.favorite_filter.get(): items = [i for i in items if self.item_is_favorite(i)]
        if query:
            items = [i for i in items if query in i.name.lower() or query in i.category.lower() or query in i.relative.lower() or any(query in t.lower() for t in self.item_tags(i))]
        self.library_info.configure(text=f"Projektordner: {self.project_folder.get() or '(nicht gesetzt)'}    Treffer: {len(items)}    Gesamt: {len(self.library_items)}")
        if not items:
            ctk.CTkLabel(self.library_grid, text="Keine Treffer. Prüfe Projektordner, Filter oder Suche.", text_color="#BCA870").grid(row=0, column=0, padx=18, pady=18, sticky="w")
            return
        cols = 4
        for idx, item in enumerate(items):
            r, c = divmod(idx, cols)
            border = GOLD if self.selected_item and self.item_key(self.selected_item) == self.item_key(item) else "#151515"
            card = ctk.CTkFrame(self.library_grid, fg_color="#151515", corner_radius=10, border_color=border, border_width=2)
            card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")
            star = "⭐ " if self.item_is_favorite(item) else ""
            prof = " ✓" if item.section == "Banners" and has_profile(self.banner_profiles, self.item_key(item)) else ""
            ctk.CTkLabel(card, text=star + item.section + prof, text_color=GOLD if star else "#BCA870", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=10, pady=(8, 0))
            img_label = self.make_thumb_label(card, item.path)
            img_label.pack(padx=10, pady=(6, 6))
            for widget in [card, img_label]:
                widget.bind("<Button-1>", lambda e, it=item: self.select_library_item(it))
                widget.bind("<Double-Button-1>", lambda e, it=item: self.library_item_double_click(it))
            name_label = ctk.CTkLabel(card, text=item.name, text_color=TEXT, wraplength=210, justify="center")
            name_label.pack(padx=10, pady=(0, 2))
            for widget in [name_label]:
                widget.bind("<Button-1>", lambda e, it=item: self.select_library_item(it))
                widget.bind("<Double-Button-1>", lambda e, it=item: self.library_item_double_click(it))
            ctk.CTkLabel(card, text=item.category, text_color="#BCA870", wraplength=210, justify="center", font=ctk.CTkFont(size=12)).pack(padx=10, pady=(0, 4))
            ctk.CTkLabel(card, text=", ".join(self.item_tags(item)[:4]), text_color="#8F8058", wraplength=210, justify="center", font=ctk.CTkFont(size=11)).pack(padx=10, pady=(0, 10))

    def make_thumb_label(self, parent, path):
        try:
            if path.suffix.lower() in [".png", ".jpg", ".jpeg", ".webp"]:
                img = Image.open(path).convert("RGBA")
                img.thumbnail((220, 124))
                thumb = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                self.thumbnail_refs.append(thumb)
                return ctk.CTkLabel(parent, image=thumb, text="")
            return ctk.CTkLabel(parent, text="♪ SOUND", text_color=GOLD, width=220, height=124, fg_color="#050505", corner_radius=8)
        except Exception:
            return ctk.CTkLabel(parent, text="[kann nicht geladen werden]", text_color="#D86A6A", width=220, height=124)

    def select_library_item(self, item):
        self.selected_item = item
        self.preview_refs = []
        if hasattr(self, "selection_preview"):
            for w in self.selection_preview.winfo_children(): w.destroy()
        try:
            if item.kind == "image":
                img = Image.open(item.path).convert("RGBA")
                img.thumbnail((320, 280))
                preview = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
                self.preview_refs.append(preview)
                ctk.CTkLabel(self.selection_preview, image=preview, text="").place(relx=0.5, rely=0.5, anchor="center")
            else:
                ctk.CTkLabel(self.selection_preview, text="♪ SOUND", text_color=GOLD, font=ctk.CTkFont(size=28, weight="bold")).place(relx=0.5, rely=0.5, anchor="center")
        except Exception:
            ctk.CTkLabel(self.selection_preview, text="Asset kann nicht geladen werden", text_color="#D86A6A").place(relx=0.5, rely=0.5, anchor="center")
        fav = "⭐ " if self.item_is_favorite(item) else ""
        self.selection_name.configure(text=fav + item.name)
        tags = ", ".join(self.item_tags(item)) or "keine"
        self.selection_meta.configure(text=f"{item.section} / {item.category}\n{item.relative}\nTags: {tags}\nTyp: {item.kind}")
        self.render_library_grid()

    def library_item_double_click(self, item):
        self.select_library_item(item)
        self.default_selected_action()

    def default_selected_action(self):
        if not self.selected_item:
            messagebox.showwarning("Library", "Bitte zuerst ein Asset auswählen.")
            return
        item = self.selected_item
        if item.section == "Banners": self.use_selected_as_caption_banner()
        elif item.section == "Live Cards": self.open_selected_live_card()
        elif item.section == "Templates": self.assign_selected_template_background()
        elif item.section == "Sounds": self.open_selected_file()
        else: self.show_selected_scene_card()







    def template_set_background_path(self, path):
        if not path:
            return
        data, dest = set_background_from_file(self.template_selected_name, path)
        self.template_working_data = data

        if hasattr(self, "template_canvas"):
            self.template_draw_canvas()
        try:
            self.template_canvas.focus_set()
        except Exception:
            pass
        return dest


    def assign_selected_template_background(self):
        item = getattr(self, "selected_item", None)
        if item is None:
            messagebox.showwarning("Template Background", "Bitte zuerst in der Library ein Template-Bild auswählen.")
            return
        if getattr(item, "kind", "") != "image":
            messagebox.showwarning("Template Background", "Bitte ein Bild aus der Library auswählen.")
            return
        self.template_set_background_path(item.path)
        messagebox.showinfo(
            "Template Background",
            f"Hintergrundbild gespeichert:\n\nTemplate: {self.template_selected_name}\nBild: {Path(item.path).name}"
        )


    def use_selected_as_caption_banner(self):
        if not self.selected_item: return
        if self.selected_item.kind != "image":
            messagebox.showwarning("Banner", "Nur Bilder können als Caption-Banner verwendet werden.")
            return
        self.config_data["selected_banner_path"] = str(self.selected_item.path)
        save_config(self.config_data)
        if self.ensure_obs_ready():
            try:
                self.obs.set_image_file(self.caption_banner_source.get().strip(), self.selected_item.path)
                if hasattr(self, "message_box"):
                    self.update_render_preview()
                messagebox.showinfo("Banner", f"Caption-Banner gewechselt:\n{self.selected_item.name}")
            except Exception:
                if hasattr(self, "message_box"):
                    self.update_render_preview()
                messagebox.showwarning(
                    "Caption Banner Source nicht gefunden",
                    f"Banner wurde im Studio gespeichert, aber die OBS-Bildquelle '{self.caption_banner_source.get().strip()}' wurde nicht gefunden.\n\nFür smart_png ist vor allem 'VADAFOK Caption Render' wichtig."
                )

    def show_selected_scene_card(self):
        if not self.selected_item: return
        if self.selected_item.kind != "image":
            messagebox.showwarning("Scene Card", "Nur Bilder können als Scene Card angezeigt werden.")
            return
        if not self.obs.connected:
            messagebox.showwarning("Nicht verbunden", "Bitte zuerst OBS verbinden.")
            return
        try:
            scene = self.current_scene()
            source = self.scene_card_source.get().strip()
            self.obs.set_image_file(source, self.selected_item.path)
            self.obs.enable_source(scene, source, True)
        except Exception as e:
            messagebox.showerror("Scene Card fehlgeschlagen", str(e))

    def open_selected_live_card(self):
        if not self.selected_item: return
        self.show_live_card()
        self.set_message(self.selected_item.path.stem.replace("_", " ").replace("-", " ").upper())

    def toggle_selected_favorite(self):
        if not self.selected_item:
            messagebox.showwarning("Library", "Bitte zuerst ein Asset auswählen.")
            return
        key = self.item_key(self.selected_item)
        favs = self.asset_meta.setdefault("favorites", [])
        if key in favs: favs.remove(key)
        else: favs.append(key)
        save_asset_meta(self.asset_meta)
        self.select_library_item(self.selected_item)

    def edit_selected_tags(self):
        if not self.selected_item:
            messagebox.showwarning("Library", "Bitte zuerst ein Asset auswählen.")
            return
        key = self.item_key(self.selected_item)
        current = ", ".join(self.asset_meta.setdefault("tags", {}).get(key, []))
        result = simpledialog.askstring("Tags", "Tags mit Komma trennen:", initialvalue=current)
        if result is None: return
        self.asset_meta.setdefault("tags", {})[key] = [t.strip() for t in result.split(",") if t.strip()]
        save_asset_meta(self.asset_meta)
        self.select_library_item(self.selected_item)

    def open_selected_folder(self):
        if self.selected_item: os.startfile(self.selected_item.path.parent)

    def open_selected_file(self):
        if self.selected_item: os.startfile(self.selected_item.path)

    def copy_selected_path(self):
        if not self.selected_item: return
        self.clipboard_clear()
        self.clipboard_append(str(self.selected_item.path))
        messagebox.showinfo("Copy Path", "Pfad kopiert.")




    def show_banner_profiles_page(self):
        self.set_active("Banner Editor")
        self.clear_main()
        self.page_title("Banner Editor")

        self.library_items = scan_library(self.project_folder.get())
        banners = [i for i in self.library_items if i.section == "Banners" and i.kind == "image"]

        outer = ctk.CTkFrame(self.main, fg_color=DARK)
        outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_columnconfigure(1, weight=4)
        outer.grid_columnconfigure(2, weight=1)
        outer.grid_columnconfigure(3, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(left, text="Banner", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")
        banner_list = ctk.CTkScrollableFrame(left, fg_color="#0B0B0B", corner_radius=12)
        banner_list.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))

        if not banners:
            ctk.CTkLabel(banner_list, text="Keine Banner gefunden.", text_color="#BCA870").pack(anchor="w", padx=12, pady=12)
        else:
            for item in banners:
                status = "✓ " if has_profile(self.banner_profiles, item.relative) else "⚠ "
                ctk.CTkButton(
                    banner_list,
                    text=status + item.name,
                    anchor="w",
                    height=38,
                    fg_color="#171717",
                    hover_color="#2C2C2C",
                    command=lambda it=item: self.editor_select_banner(it)
                ).pack(fill="x", padx=8, pady=4)

        right = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(right, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Textbereich mit der Maus setzen", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w")
        self.editor_status_label = ctk.CTkLabel(header, text="Noch kein Banner ausgewählt", text_color="#BCA870", anchor="e")
        self.editor_status_label.grid(row=0, column=1, sticky="e")

        self.editor_preview_frame = ctk.CTkFrame(right, fg_color="#050505", corner_radius=14, border_color="#3A2A0D", border_width=1)
        self.editor_preview_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 12))
        self.editor_preview_frame.grid_columnconfigure(0, weight=1)
        self.editor_preview_frame.grid_rowconfigure(0, weight=1)

        self.editor_canvas = tk.Canvas(self.editor_preview_frame, bg="#050505", highlightthickness=0, cursor="crosshair")
        self.editor_canvas.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.editor_canvas.bind("<ButtonPress-1>", self.editor_mouse_down)
        self.editor_canvas.bind("<B1-Motion>", self.editor_mouse_drag)
        self.editor_canvas.bind("<ButtonRelease-1>", self.editor_mouse_up)
        self.editor_canvas.bind("<Motion>", self.editor_mouse_motion)

        controls = ctk.CTkScrollableFrame(right, fg_color="#0B0B0B", corner_radius=12)
        controls.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))
        controls.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(controls, text="Sample Text", text_color="#BCA870").grid(row=0, column=0, padx=(0, 8), pady=4, sticky="w")
        sample_entry = ctk.CTkEntry(controls, textvariable=self.editor_sample_text)
        sample_entry.grid(row=0, column=1, padx=(0, 8), pady=4, sticky="ew")
        sample_entry.bind("<KeyRelease>", lambda e: self.editor_update_overlay())
        ctk.CTkLabel(controls, text="Font", text_color="#BCA870").grid(row=1, column=0, padx=(12, 8), pady=4, sticky="w")
        font_entry = ctk.CTkEntry(controls, textvariable=self.editor_font_family)
        font_entry.grid(row=1, column=1, padx=(0, 8), pady=4, sticky="ew")
        font_entry.bind("<KeyRelease>", lambda e: self.editor_apply_profile_values())

        ctk.CTkLabel(controls, text="Size", text_color="#BCA870").grid(row=1, column=2, padx=(12, 8), pady=4, sticky="w")
        size_entry = ctk.CTkEntry(controls, textvariable=self.editor_font_size)
        size_entry.grid(row=1, column=3, padx=(0, 8), pady=4, sticky="ew")
        size_entry.bind("<KeyRelease>", lambda e: self.editor_apply_profile_values())

        ctk.CTkLabel(controls, text="Text", text_color="#BCA870").grid(row=2, column=0, padx=(12, 8), pady=4, sticky="w")
        tc_entry = ctk.CTkEntry(controls, textvariable=self.editor_text_color)
        tc_entry.grid(row=2, column=1, padx=(0, 8), pady=4, sticky="ew")
        tc_entry.bind("<KeyRelease>", lambda e: self.editor_apply_profile_values())

        ctk.CTkLabel(controls, text="Stroke", text_color="#BCA870").grid(row=2, column=2, padx=(12, 8), pady=4, sticky="w")
        sc_entry = ctk.CTkEntry(controls, textvariable=self.editor_stroke_color)
        sc_entry.grid(row=2, column=3, padx=(0, 8), pady=4, sticky="ew")
        sc_entry.bind("<KeyRelease>", lambda e: self.editor_apply_profile_values())

        ctk.CTkLabel(controls, text="Stroke Width", text_color="#BCA870").grid(row=3, column=0, padx=(12, 8), pady=4, sticky="w")
        sw_entry = ctk.CTkEntry(controls, textvariable=self.editor_stroke_width)
        sw_entry.grid(row=3, column=1, padx=(0, 8), pady=4, sticky="ew")
        sw_entry.bind("<KeyRelease>", lambda e: self.editor_apply_profile_values())

        ctk.CTkCheckBox(controls, text="Uppercase", variable=self.editor_uppercase, text_color=TEXT, command=self.editor_apply_profile_values).grid(row=3, column=2, padx=(12, 8), pady=4, sticky="w")


        ctk.CTkButton(controls, text="SAVE PROFILE", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=self.editor_save_profile).grid(row=4, column=0, columnspan=2, padx=4, pady=8, sticky="ew")
        ctk.CTkButton(controls, text="RESET AREA", fg_color="#333333", hover_color="#444444", command=self.editor_reset_area).grid(row=4, column=2, padx=4, pady=8, sticky="ew")
        ctk.CTkButton(controls, text="RESET STYLE", fg_color="#333333", hover_color="#444444", command=self.editor_reset_style).grid(row=4, column=3, padx=4, pady=8, sticky="ew")

        ctk.CTkLabel(
            right,
            text="Phase C: Ziehe den goldenen Rahmen direkt im Banner. Ziehen in der Mitte verschiebt, Ziehen an den Ecken/Kanten verändert die Größe.",
            text_color="#D9C58C",
            wraplength=820,
            justify="left"
        ).grid(row=3, column=0, sticky="w", padx=18, pady=(0, 18))

        if self.editor_selected_banner is None and banners:
            self.editor_select_banner(banners[0])
        elif self.editor_selected_banner is not None:
            self.editor_draw_canvas()

    def editor_select_banner(self, item):
        self.editor_selected_banner = item
        profile = ensure_profile(self.banner_profiles, item.relative)
        self.editor_load_profile_values(profile)
        if not profile["text_area"]["width"] or not profile["text_area"]["height"]:
            try:
                img = Image.open(item.path).convert("RGBA")
                w, h = img.size
                profile["text_area"] = {"x": int(w * 0.12), "y": int(h * 0.24), "width": int(w * 0.76), "height": int(h * 0.52)}
                save_banner_profiles(self.banner_profiles)
            except Exception:
                pass
        self.editor_draw_canvas()

    def editor_profile(self):
        if not self.editor_selected_banner:
            return None
        return ensure_profile(self.banner_profiles, self.editor_selected_banner.relative)


    def editor_load_profile_values(self, profile):
        self.editor_font_family.set(profile.get("font_family", self.caption_font_family.get()))
        self.editor_font_size.set(int(profile.get("font_size", self.caption_font_size.get())))
        self.editor_text_color.set(profile.get("text_color", self.caption_text_color.get()))
        self.editor_stroke_color.set(profile.get("stroke_color", self.caption_stroke_color.get()))
        self.editor_stroke_width.set(int(profile.get("stroke_width", self.caption_stroke_width.get())))
        self.editor_uppercase.set(bool(profile.get("uppercase", self.caption_uppercase.get())))

    def editor_apply_profile_values(self):
        profile = self.editor_profile()
        if not profile:
            return
        try:
            profile["font_family"] = self.editor_font_family.get()
            profile["font_size"] = int(self.editor_font_size.get())
            profile["text_color"] = self.editor_text_color.get()
            profile["stroke_color"] = self.editor_stroke_color.get()
            profile["stroke_width"] = int(self.editor_stroke_width.get())
            profile["uppercase"] = bool(self.editor_uppercase.get())
            save_banner_profiles(self.banner_profiles)
            self.editor_update_overlay()
        except Exception:
            pass

    def editor_save_profile(self):
        if not self.editor_selected_banner:
            messagebox.showwarning("Banner Editor", "Bitte zuerst ein Banner auswählen.")
            return
        self.editor_apply_profile_values()
        profile = self.editor_profile()
        if profile:
            field = banner_profile_to_layout_field(profile)
            apply_layout_field_to_banner_profile(profile, field)
        save_banner_profiles(self.banner_profiles)
        messagebox.showinfo("Banner Editor", f"Profil gespeichert:\n{self.editor_selected_banner.name}")
        self.show_banner_profiles_page()


    def editor_reset_style(self):
        if not self.editor_selected_banner:
            return
        profile = self.editor_profile()
        reset_profile_style(profile)
        self.editor_load_profile_values(profile)
        save_banner_profiles(self.banner_profiles)
        self.editor_update_overlay()
        messagebox.showinfo("Banner Editor", "Profilwerte wurden auf Standard zurückgesetzt.")

    def editor_reset_area(self):
        if not self.editor_selected_banner:
            return
        profile = self.editor_profile()
        img = Image.open(self.editor_selected_banner.path).convert("RGBA")
        w, h = img.size
        profile["text_area"] = {"x": int(w * 0.12), "y": int(h * 0.24), "width": int(w * 0.76), "height": int(h * 0.52)}
        save_banner_profiles(self.banner_profiles)
        self.editor_draw_canvas()


    def editor_draw_canvas(self, full_redraw=True):
        """
        Anti-flicker drawing:
        - full_redraw=True loads/scales the banner once.
        - full_redraw=False updates only overlay rectangle, handles, and sample text.
        """
        if not hasattr(self, "editor_canvas") or not self.editor_selected_banner:
            return

        if full_redraw or self.editor_banner_image_id is None:
            self.editor_redraw_banner()
        self.editor_update_overlay()

    def editor_redraw_banner(self):
        canvas = self.editor_canvas
        canvas.delete("all")
        self.editor_handle_ids = []
        self.editor_area_rect_id = None
        self.editor_sample_text_id = None

        banner = Image.open(self.editor_selected_banner.path).convert("RGBA")
        bw, bh = banner.size
        self.editor_canvas_banner_size = (bw, bh)

        canvas.update_idletasks()
        cw = max(400, canvas.winfo_width())
        ch = max(260, canvas.winfo_height())
        scale = min((cw - 30) / bw, (ch - 30) / bh)
        self.editor_canvas_scale = scale

        display_w = int(bw * scale)
        display_h = int(bh * scale)
        offset_x = (cw - display_w) // 2
        offset_y = (ch - display_h) // 2
        self.editor_canvas_offset = (offset_x, offset_y)

        display = banner.resize((display_w, display_h))
        self.editor_canvas_photo = tk.PhotoImage(data=self._pil_to_png_bytes(display))
        self.editor_banner_image_id = canvas.create_image(
            offset_x,
            offset_y,
            image=self.editor_canvas_photo,
            anchor="nw",
            tags="banner"
        )

    def editor_update_overlay(self):
        canvas = self.editor_canvas
        if not self.editor_selected_banner:
            return

        profile = self.editor_profile()
        if not profile:
            return

        # Delete overlay only. Do NOT delete banner image. This prevents flicker.
        for item_id in [self.editor_area_rect_id, self.editor_sample_text_id]:
            if item_id:
                try:
                    canvas.delete(item_id)
                except Exception:
                    pass

        for item_id in self.editor_handle_ids:
            try:
                canvas.delete(item_id)
            except Exception:
                pass
        self.editor_handle_ids = []

        ox, oy = self.editor_canvas_offset
        s = self.editor_canvas_scale
        area = profile["text_area"]

        x1 = ox + int(area["x"] * s)
        y1 = oy + int(area["y"] * s)
        x2 = ox + int((area["x"] + area["width"]) * s)
        y2 = oy + int((area["y"] + area["height"]) * s)

        self.editor_area_rect_id = canvas.create_rectangle(
            x1, y1, x2, y2,
            fill="#D6A43A",
            stipple="gray25",
            outline=GOLD,
            width=3,
            tags="area"
        )

        text = (self.editor_sample_text.get() or "HELLO WORLD")
        if self.editor_uppercase.get():
            text = text.upper()
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        self.editor_sample_text_id = canvas.create_text(
            cx, cy,
            text=text,
            fill=self.editor_text_color.get(),
            font=("Arial", max(10, min(42, int(self.editor_font_size.get() / 5))), "bold"),
            width=max(50, x2 - x1 - 20),
            justify="center",
            tags="sample"
        )

        for hx, hy in self.editor_handle_points(x1, y1, x2, y2):
            hid = canvas.create_rectangle(
                hx - 6, hy - 6, hx + 6, hy + 6,
                fill=GOLD,
                outline="#111111",
                tags="handle"
            )
            self.editor_handle_ids.append(hid)

        if hasattr(self, "editor_status_label"):
            self.editor_status_label.configure(
                text=f"✓ {self.editor_selected_banner.name} | Bereich {area['width']}×{area['height']}",
                text_color="#8FE6A0"
            )

    def _pil_to_png_bytes(self, image):
        import io, base64
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        return base64.b64encode(buf.getvalue())

    def editor_draw_sample_text(self, canvas, x1, y1, x2, y2):
        text = (self.editor_sample_text.get() or "HELLO WORLD")
        if self.editor_uppercase.get():
            text = text.upper()
        cx = (x1 + x2) // 2
        cy = (y1 + y2) // 2
        canvas.create_text(cx, cy, text=text, fill="white", font=("Arial", 22, "bold"), width=max(50, x2-x1-20), justify="center", tags="sample")

    def editor_handle_points(self, x1, y1, x2, y2):
        return [
            (x1, y1), ((x1+x2)//2, y1), (x2, y1),
            (x1, (y1+y2)//2), (x2, (y1+y2)//2),
            (x1, y2), ((x1+x2)//2, y2), (x2, y2)
        ]

    def editor_hit_test(self, x, y):
        profile = self.editor_profile()
        if not profile:
            return None
        ox, oy = self.editor_canvas_offset
        s = self.editor_canvas_scale
        area = profile["text_area"]
        x1 = ox + area["x"] * s
        y1 = oy + area["y"] * s
        x2 = ox + (area["x"] + area["width"]) * s
        y2 = oy + (area["y"] + area["height"]) * s
        tol = 10

        near_left = abs(x - x1) <= tol
        near_right = abs(x - x2) <= tol
        near_top = abs(y - y1) <= tol
        near_bottom = abs(y - y2) <= tol

        if near_left and near_top: return "nw"
        if near_right and near_top: return "ne"
        if near_left and near_bottom: return "sw"
        if near_right and near_bottom: return "se"
        if near_left and y1 <= y <= y2: return "w"
        if near_right and y1 <= y <= y2: return "e"
        if near_top and x1 <= x <= x2: return "n"
        if near_bottom and x1 <= x <= x2: return "s"
        if x1 <= x <= x2 and y1 <= y <= y2: return "move"
        return "new"


    def editor_mouse_motion(self, event):
        if not self.editor_selected_banner:
            return
        mode = self.editor_hit_test(event.x, event.y)
        cursor = "crosshair"
        if mode == "move":
            cursor = "fleur"
        elif mode in ("nw", "se"):
            cursor = "size_nw_se"
        elif mode in ("ne", "sw"):
            cursor = "size_ne_sw"
        elif mode in ("n", "s"):
            cursor = "sb_v_double_arrow"
        elif mode in ("e", "w"):
            cursor = "sb_h_double_arrow"
        self.editor_canvas.configure(cursor=cursor)

    def editor_mouse_down(self, event):
        if not self.editor_selected_banner:
            return
        self.editor_drag_mode = self.editor_hit_test(event.x, event.y)
        self.editor_drag_start = (event.x, event.y)
        profile = self.editor_profile()
        self.editor_drag_original = dict(profile["text_area"])

        if self.editor_drag_mode == "new":
            ox, oy = self.editor_canvas_offset
            s = self.editor_canvas_scale
            bx = int((event.x - ox) / s)
            by = int((event.y - oy) / s)
            profile["text_area"] = {"x": bx, "y": by, "width": 1, "height": 1}
            self.editor_drag_original = dict(profile["text_area"])

    def editor_mouse_drag(self, event):
        if not self.editor_drag_mode or not self.editor_selected_banner:
            return

        profile = self.editor_profile()
        area = dict(self.editor_drag_original)
        sx, sy = self.editor_drag_start
        dx = int((event.x - sx) / self.editor_canvas_scale)
        dy = int((event.y - sy) / self.editor_canvas_scale)
        bw, bh = self.editor_canvas_banner_size
        mode = self.editor_drag_mode

        x, y, w, h = area["x"], area["y"], area["width"], area["height"]

        if mode == "move":
            x += dx
            y += dy
        elif mode == "new":
            w = dx
            h = dy
        else:
            if "w" in mode:
                x += dx
                w -= dx
            if "e" in mode:
                w += dx
            if "n" in mode:
                y += dy
                h -= dy
            if "s" in mode:
                h += dy

        if w < 0:
            x += w
            w = abs(w)
        if h < 0:
            y += h
            h = abs(h)

        x = max(0, min(bw - 20, x))
        y = max(0, min(bh - 20, y))
        w = max(20, min(bw - x, w))
        h = max(20, min(bh - y, h))

        profile["text_area"] = {"x": int(x), "y": int(y), "width": int(w), "height": int(h)}
        self.editor_update_overlay()

    def editor_mouse_up(self, event):
        if self.editor_selected_banner:
            save_banner_profiles(self.banner_profiles)
        self.editor_drag_mode = None
        self.editor_drag_start = None
        self.editor_drag_original = None

    def show_live_card(self):
        self.set_active("Live Card")
        self.clear_main()
        self.page_title("Live Card")
        content = ctk.CTkFrame(self.main, fg_color=DARK)
        content.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(content, fg_color=PANEL, corner_radius=18)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_columnconfigure(0, weight=1)
        left.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(left, text="Message", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT).grid(row=0, column=0, padx=18, pady=(18, 6), sticky="w")
        self.message_box = ctk.CTkTextbox(left, height=180, font=ctk.CTkFont(size=18), fg_color="#050505", border_color=GOLD_DARK, border_width=1)
        self.message_box.grid(row=1, column=0, padx=18, pady=(0, 12), sticky="nsew")
        self.message_box.insert("1.0", self.live_card_pending_text or "CHAT WAS RIGHT.")
        self.message_box.bind("<Return>", self.enter_to_show)
        self.message_box.bind("<KeyRelease>", lambda e: self.update_render_preview())

        row = ctk.CTkFrame(left, fg_color="transparent")
        row.grid(row=2, column=0, sticky="ew", padx=18, pady=8)
        row.grid_columnconfigure((0, 1, 2), weight=1)
        self.option(row, "Engine", ["obs_text", "smart_png"], self.caption_engine, 0)
        self.option(row, "Style", list(self.config_data["banner_sources"].keys()), self.style, 1)
        self.option(row, "Duration", ["3", "5", "7", "10", "15"], self.duration, 2)

        btns = ctk.CTkFrame(left, fg_color="transparent")
        btns.grid(row=3, column=0, sticky="ew", padx=18, pady=(14, 18))
        btns.grid_columnconfigure((0, 1, 2, 3), weight=1)
        ctk.CTkButton(btns, text="SHOW", height=46, fg_color=GOLD, hover_color=GOLD_DARK, text_color="#111111", command=self.show_card).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(btns, text="HIDE", height=46, fg_color="#333333", command=self.hide_card).grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkButton(btns, text="CLEAR", height=46, fg_color="#222222", command=self.clear_text).grid(row=0, column=2, padx=5, sticky="ew")
        ctk.CTkButton(btns, text="SAVE QUICK", height=46, fg_color="#222222", command=self.save_current_quick).grid(row=0, column=3, padx=5, sticky="ew")

        quick_save_box = ctk.CTkFrame(left, fg_color="#0B0B0B", corner_radius=10)
        quick_save_box.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 12))
        quick_save_box.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(quick_save_box, text="Quick Save Category", text_color="#BCA870").grid(row=0, column=0, padx=(10, 8), pady=10, sticky="w")
        cats = self.quick_cards_categories()
        if self.quick_cards_target_category.get() not in cats:
            self.quick_cards_target_category.set("Chat" if "Chat" in cats else cats[0])
        ctk.CTkOptionMenu(
            quick_save_box,
            values=cats,
            variable=self.quick_cards_target_category,
            fg_color="#333333",
            button_color="#444444",
            button_hover_color="#555555"
        ).grid(row=0, column=1, padx=(0, 10), pady=10, sticky="ew")

        right = ctk.CTkFrame(content, fg_color=PANEL, corner_radius=18)
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right.grid_rowconfigure(1, weight=1)
        right.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(right, text="Live Preview", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")
        self.preview_frame = ctk.CTkFrame(right, fg_color="#020202", corner_radius=14, border_width=1, border_color="#3A2A0D")
        self.preview_frame.grid(row=1, column=0, padx=18, pady=(0, 8), sticky="nsew")

        self.render_status_label = ctk.CTkLabel(
            right,
            text="Preview wartet...",
            text_color="#BCA870",
            justify="left",
            anchor="w"
        )
        self.render_status_label.grid(row=2, column=0, padx=18, pady=(0, 8), sticky="ew")

        ctk.CTkButton(
            right,
            text="REFRESH PREVIEW",
            fg_color="#333333",
            hover_color="#444444",
            command=self.update_render_preview
        ).grid(row=3, column=0, padx=18, pady=(0, 18), sticky="ew")

        self.update_render_preview()

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
            save_template(self.template_selected_name, template)
            self.template_draw_canvas()
        except Exception:
            pass




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
        self.assign_selected_template_background()



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
            self.template_draw_canvas()

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
            self.template_draw_canvas()



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
        state = int(getattr(event, "state", 0) or 0)

        # Tk modifier masks differ a bit by platform/theme.
        # Common masks:
        # Shift = 0x0001
        # Ctrl  = 0x0004
        # Also use our explicit key state fallback.
        return (
            bool(state & 0x0001)
            or bool(state & 0x0004)
            or bool(getattr(self, "template_shift_down", False))
            or bool(getattr(self, "template_ctrl_down", False))
        )



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
        self.template_layer_drag_index = idx
        self.template_layer_drag_start_y = getattr(event, "y_root", 0)
        self.template_layer_drop_target = None

        try:
            event.widget.configure(fg_color=GOLD, text_color="#111111")
        except Exception:
            pass

        return "break"

    def template_layer_clear_drop_indicator(self):
        if hasattr(self, "template_layer_drop_indicator") and self.template_layer_drop_indicator is not None:
            try:
                self.template_layer_drop_indicator.destroy()
            except Exception:
                pass
        self.template_layer_drop_indicator = None

    def template_layer_drag_motion(self, event):
        try:
            self.template_layers_body.configure(cursor="hand2")
        except Exception:
            pass

        target_idx = self.template_layer_target_from_y(getattr(event, "y_root", 0))
        self.template_layer_drop_target = target_idx
        self.template_layer_show_drop_indicator(target_idx)

        return "break"

    def template_layer_show_drop_indicator(self, target_idx):
        self.template_layer_clear_drop_indicator()

        if target_idx is None:
            return

        try:
            row = self._template_layer_row_for_field.get(target_idx)
            if row is None:
                return

            # Add a thin gold bar above the target row.
            indicator = ctk.CTkFrame(
                self.template_layers_body,
                height=4,
                fg_color=GOLD,
                corner_radius=2
            )
            indicator.grid(row=row, column=0, columnspan=5, padx=8, pady=(0, 0), sticky="ew")
            try:
                indicator.lift()
            except Exception:
                pass

            self.template_layer_drop_indicator = indicator
        except Exception:
            self.template_layer_drop_indicator = None

    def template_layer_drag_end(self, event):
        try:
            self.template_layers_body.configure(cursor="")
        except Exception:
            pass

        self.template_layer_clear_drop_indicator()

        source_idx = getattr(self, "template_layer_drag_index", None)
        self.template_layer_drag_index = None

        if source_idx is None:
            self.template_build_layers_panel()
            return "break"

        target_idx = getattr(self, "template_layer_drop_target", None)
        if target_idx is None:
            target_idx = self.template_layer_target_from_y(getattr(event, "y_root", 0))

        self.template_layer_drop_target = None

        if target_idx is None or target_idx == source_idx:
            self.template_build_layers_panel()
            return "break"

        self.template_move_layer_to_index(source_idx, target_idx)
        return "break"

    def template_layer_target_from_y(self, y_root):
        if not hasattr(self, "_template_layer_row_for_field"):
            return None

        best_idx = None
        best_dist = None

        for idx, row in self._template_layer_row_for_field.items():
            try:
                widgets = self.template_layers_body.grid_slaves(row=row, column=0)
                if not widgets:
                    continue
                widget = widgets[0]
                center = widget.winfo_rooty() + widget.winfo_height() / 2
                dist = abs(center - y_root)
                if best_dist is None or dist < best_dist:
                    best_dist = dist
                    best_idx = idx
            except Exception:
                continue

        return best_idx


    def template_move_layer_to_index(self, source_idx, target_idx):
        template = self.template_current()
        fields = template.get("fields", [])

        if not (0 <= source_idx < len(fields)) or not (0 <= target_idx < len(fields)):
            return

        if source_idx == target_idx:
            return

        if hasattr(self, "template_push_history"):
            self.template_push_history("drag layer reorder")

        item = fields.pop(source_idx)
        fields.insert(target_idx, item)

        # Update selected indices after list move.
        def remap(old_idx):
            if old_idx == source_idx:
                return target_idx
            if source_idx < target_idx:
                if source_idx < old_idx <= target_idx:
                    return old_idx - 1
            else:
                if target_idx <= old_idx < source_idx:
                    return old_idx + 1
            return old_idx

        selected = set(getattr(self, "template_selected_fields", set()))
        self.template_selected_fields = {remap(i) for i in selected if 0 <= i < len(fields)}
        if self.template_selected_field is not None:
            self.template_selected_field = remap(self.template_selected_field)

        # Groups use stable field ids, so no group remap is needed.
        save_template(self.template_selected_name, template)
        self.template_draw_canvas()
        self.template_build_layers_panel()
        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()


    def template_build_layers_panel(self):
        if not hasattr(self, "template_layers_body"):
            return

        for w in self.template_layers_body.winfo_children():
            w.destroy()

        template = self.template_current()
        try:
            self.template_clean_groups()
        except Exception:
            pass

        self._template_layer_row_for_group = {}
        self._template_layer_row_for_field = {}

        fields = template.get("fields", [])
        selected = set(getattr(self, "template_selected_fields", set()))
        if self.template_selected_field is not None:
            selected.add(self.template_selected_field)

        row = 0

        if not fields:
            ctk.CTkLabel(
                self.template_layers_body,
                text="Keine Felder",
                text_color="#777777",
                wraplength=160,
                justify="left"
            ).grid(row=0, column=0, columnspan=5, padx=8, pady=8, sticky="w")
            return

        # Group headers first.
        groups = template.get("groups", [])
        selected_group_ids = self.template_selected_group_ids() if hasattr(self, "template_selected_group_ids") else set()

        for group in groups:
            group_id = group.get("id")
            self._template_layer_row_for_group[group_id] = row

            active_group = group_id in selected_group_ids
            group_hidden = bool(group.get("hidden", False))
            group_locked = bool(group.get("locked", False))
            collapsed = self.template_group_is_collapsed(group_id)
            label = ("✓ " if active_group else "") + "📦 " + group.get("name", "Group")

            ctk.CTkButton(
                self.template_layers_body,
                text="▶" if collapsed else "▼",
                width=38,
                fg_color="#333333",
                hover_color="#444444",
                command=lambda gid=group_id: self.template_toggle_group_collapsed(gid)
            ).grid(row=row, column=0, padx=(8, 2), pady=(6, 3), sticky="ew")

            group_btn = ctk.CTkButton(
                self.template_layers_body,
                text=label,
                fg_color=GOLD if active_group else "#202020",
                text_color="#111111" if active_group else "#D9C58C",
                hover_color=GOLD_DARK if active_group else "#303030",
                anchor="w",
                command=lambda gid=group_id: self.template_select_group(gid)
            )
            group_btn.grid(row=row, column=1, padx=(2, 4), pady=(6, 3), sticky="ew")

            ctk.CTkButton(
                self.template_layers_body,
                text="✎",
                width=32,
                fg_color="#333333",
                hover_color="#444444",
                command=lambda gid=group_id: self.template_rename_group(gid)
            ).grid(row=row, column=2, padx=2, pady=(6, 3), sticky="ew")

            ctk.CTkButton(
                self.template_layers_body,
                text="👁" if not group_hidden else "🚫",
                width=40,
                height=32,
                fg_color="#333333" if not group_hidden else "#5A1F1F",
                hover_color="#444444" if not group_hidden else "#7A2A2A",
                command=lambda gid=group_id: self.template_toggle_group_hidden(gid)
            ).grid(row=row, column=3, padx=2, pady=(6, 3), sticky="ew")

            ctk.CTkButton(
                self.template_layers_body,
                text="🔒" if group_locked else "○",
                width=40,
                height=32,
                fg_color="#5A1F1F" if group_locked else "#333333",
                hover_color="#7A2A2A" if group_locked else "#444444",
                command=lambda gid=group_id: self.template_toggle_group_lock(gid)
            ).grid(row=row, column=4, padx=(2, 8), pady=(6, 3), sticky="ew")

            row += 1

        # Fields. Hide fields from layer list only when their group is collapsed.
        for idx in reversed(range(len(fields))):
            field = fields[idx]
            if self.template_field_is_in_collapsed_group(idx):
                continue

            self._template_layer_row_for_field[idx] = row

            active = idx in selected
            locked = bool(field.get("locked", False))
            hidden = bool(field.get("hidden", False))
            group_name = self.template_group_name_for_field(idx) if hasattr(self, "template_group_name_for_field") else ""

            name = field.get("name", f"field_{idx+1}")
            if group_name:
                name = f"{name} · {group_name}"

            row_frame = ctk.CTkFrame(self.template_layers_body, fg_color="transparent")
            row_frame.grid(row=row, column=0, columnspan=5, padx=8, pady=3, sticky="ew")
            row_frame.grid_columnconfigure(0, weight=1)
            row_frame.grid_columnconfigure(1, minsize=44)
            row_frame.grid_columnconfigure(2, minsize=44)
            row_frame.grid_columnconfigure(3, minsize=40)
            row_frame.grid_columnconfigure(4, minsize=40)

            btn = ctk.CTkButton(
                row_frame,
                text=("✓ " if active else "") + ("🚫 " if hidden else "") + ("🔒 " if locked else "") + name,
                fg_color=GOLD if active else "#171717",
                text_color="#111111" if active else "#D9C58C",
                hover_color=GOLD_DARK if active else "#2C2C2C",
                anchor="w",
                command=lambda i=idx: self.template_select_layer(i)
            )
            pad_left = 16 if group_name else 0
            btn.grid(row=0, column=0, padx=(pad_left, 4), pady=0, sticky="ew")
            try:
                btn.bind("<Double-Button-1>", lambda _e, i=idx: self.template_start_inline_rename_field(i))
                btn.bind("<ButtonPress-1>", lambda e, i=idx: self.template_layer_drag_start(e, i), add="+")
                btn.bind("<B1-Motion>", self.template_layer_drag_motion, add="+")
                btn.bind("<ButtonRelease-1>", self.template_layer_drag_end, add="+")
            except Exception:
                pass

            ctk.CTkButton(
                row_frame,
                text="↑",
                width=44,
                height=32,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#333333",
                hover_color="#444444",
                command=lambda i=idx: self.template_move_layer(i, 1)
            ).grid(row=0, column=1, padx=2, pady=0, sticky="ew")

            ctk.CTkButton(
                row_frame,
                text="↓",
                width=44,
                height=32,
                font=ctk.CTkFont(size=16, weight="bold"),
                fg_color="#333333",
                hover_color="#444444",
                command=lambda i=idx: self.template_move_layer(i, -1)
            ).grid(row=0, column=2, padx=2, pady=0, sticky="ew")

            ctk.CTkButton(
                row_frame,
                text="👁" if not hidden else "🚫",
                width=40,
                height=32,
                fg_color="#333333" if not hidden else "#5A1F1F",
                hover_color="#444444" if not hidden else "#7A2A2A",
                command=lambda i=idx: self.template_toggle_field_hidden(i)
            ).grid(row=0, column=3, padx=2, pady=0, sticky="ew")

            ctk.CTkButton(
                row_frame,
                text="🔒" if locked else "○",
                width=40,
                height=32,
                fg_color="#5A1F1F" if locked else "#333333",
                hover_color="#7A2A2A" if locked else "#444444",
                command=lambda i=idx: self.template_toggle_field_lock(i)
            ).grid(row=0, column=4, padx=(2, 0), pady=0, sticky="ew")

            row += 1

        self.template_layers_body.grid_columnconfigure(0, weight=1)


    def template_select_layer(self, idx):
        self.template_set_single_selection(idx)
        self.template_load_selected_properties()
        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()
        self.template_update_fields_overlay()
        self.template_build_layers_panel()

    def template_move_layer(self, idx, direction):
        template = self.template_current()
        fields = template.get("fields", [])
        if not (0 <= idx < len(fields)):
            return

        new_idx = idx + int(direction)
        if not (0 <= new_idx < len(fields)):
            return

        if hasattr(self, "template_push_history"):
            self.template_push_history("layer order")

        fields[idx], fields[new_idx] = fields[new_idx], fields[idx]

        selected = set(getattr(self, "template_selected_fields", set()))
        updated = set()
        for s in selected:
            if s == idx:
                updated.add(new_idx)
            elif s == new_idx:
                updated.add(idx)
            else:
                updated.add(s)
        self.template_selected_fields = updated

        if self.template_selected_field == idx:
            self.template_selected_field = new_idx
        elif self.template_selected_field == new_idx:
            self.template_selected_field = idx

        save_template(self.template_selected_name, template)
        self.template_draw_canvas()
        self.template_build_layers_panel()
        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()



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
        self.set_active("Template Editor")
        self.clear_main()
        self.page_title("Template Editor")

        if not list_templates():
            create_template("Default Stream Plan")
        if self.template_selected_name not in list_templates():
            default_name = get_default_template()
            self.template_selected_name = default_name if default_name in list_templates() else list_templates()[0]

        outer = ctk.CTkFrame(self.main, fg_color=DARK)
        outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_columnconfigure(1, weight=4)
        outer.grid_columnconfigure(2, weight=1)
        outer.grid_columnconfigure(3, weight=1)
        outer.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(left, text="Templates", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")
        template_actions = ctk.CTkFrame(left, fg_color="transparent")
        template_actions.grid(row=1, column=0, padx=18, pady=(0, 8), sticky="ew")
        template_actions.grid_columnconfigure(0, weight=1)
        template_actions.grid_columnconfigure(1, weight=1)

        ctk.CTkButton(template_actions, text="+ NEW", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=self.template_create_default).grid(row=0, column=0, padx=(0, 4), pady=3, sticky="ew")
        ctk.CTkButton(template_actions, text="RENAME", fg_color="#333333", hover_color="#444444", command=self.template_rename_current).grid(row=0, column=1, padx=(4, 0), pady=3, sticky="ew")
        ctk.CTkButton(template_actions, text="DUPLICATE", fg_color="#333333", hover_color="#444444", command=self.template_duplicate_current).grid(row=1, column=0, padx=(0, 4), pady=3, sticky="ew")
        ctk.CTkButton(template_actions, text="DEFAULT", fg_color="#333333", hover_color="#444444", command=self.template_set_current_default).grid(row=1, column=1, padx=(4, 0), pady=3, sticky="ew")
        ctk.CTkButton(template_actions, text="DELETE", fg_color="#5A1F1F", hover_color="#7A2A2A", command=self.template_delete_current).grid(row=2, column=0, columnspan=2, padx=0, pady=3, sticky="ew")

        template_list = ctk.CTkScrollableFrame(left, fg_color="#0B0B0B", corner_radius=12)
        template_list.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))

        default_template_name = get_default_template()
        for name in sorted(list_templates()):
            prefix = "✓ " if name == self.template_selected_name else ""
            if name == default_template_name:
                prefix += "★ "
            ctk.CTkButton(
                template_list,
                text=prefix + name,
                anchor="w",
                fg_color="#171717",
                hover_color="#2C2C2C",
                command=lambda n=name: self.template_select(n)
            ).pack(fill="x", padx=8, pady=4)

        right = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(right, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))
        header.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(header, text="Multi-Field Layout", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w")
        self.template_status_label = ctk.CTkLabel(header, text=self.template_selected_name, text_color="#BCA870", anchor="e")
        self.template_status_label.grid(row=0, column=1, sticky="e")

        self.template_canvas_frame = ctk.CTkFrame(right, fg_color="#050505", corner_radius=14, border_color="#3A2A0D", border_width=1)
        self.template_canvas_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 12))
        self.template_canvas_frame.grid_columnconfigure(0, weight=1)
        self.template_canvas_frame.grid_rowconfigure(0, weight=1)

        self.template_canvas = tk.Canvas(self.template_canvas_frame, bg="#050505", highlightthickness=0, cursor="crosshair")
        self.template_canvas.grid(row=0, column=0, sticky="nsew", padx=12, pady=12)
        self.template_canvas.bind("<ButtonPress-1>", self.template_mouse_down)
        self.template_canvas.bind("<B1-Motion>", self.template_mouse_drag)
        self.template_canvas.bind("<ButtonRelease-1>", self.template_mouse_up)
        self.template_canvas.bind("<Motion>", self.template_mouse_motion)
        self.template_canvas.bind("<Control-MouseWheel>", self.template_mouse_wheel_zoom)
        self.template_canvas.bind("<Control-Button-4>", self.template_mouse_wheel_zoom)
        self.template_canvas.bind("<Control-Button-5>", self.template_mouse_wheel_zoom)
        self.template_canvas.bind("<KeyPress>", self.template_key_down)
        self.template_canvas.bind("<KeyPress>", self.template_keyboard_handler, add="+")
        self.template_canvas.bind("<KeyRelease>", self.template_key_up)
        self.bind("<KeyPress>", self.template_key_down)
        self.bind("<KeyPress>", self.template_keyboard_handler, add="+")
        self.bind("<KeyRelease>", self.template_key_up)
        self.template_canvas.bind("<ButtonPress-2>", self.template_pan_start_drag)
        self.template_canvas.bind("<B2-Motion>", self.template_pan_drag)
        self.template_canvas.bind("<ButtonRelease-2>", self.template_pan_end_drag)
        self.template_canvas.bind("<Shift-ButtonPress-1>", self.template_pan_start_drag)
        self.template_canvas.bind("<Shift-B1-Motion>", self.template_pan_drag)
        self.template_canvas.bind("<Shift-ButtonRelease-1>", self.template_pan_end_drag)

        controls = ctk.CTkFrame(right, fg_color="transparent")
        controls.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))
        controls.grid_columnconfigure((0,1,2,3,4), weight=1)

        ctk.CTkButton(controls, text="+ ADD FIELD", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=self.template_add_field).grid(row=0, column=0, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(controls, text="COPY FIELD", fg_color="#333333", hover_color="#444444", command=self.template_copy_field).grid(row=0, column=1, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(controls, text="DELETE FIELD", fg_color="#333333", hover_color="#444444", command=self.template_delete_field).grid(row=0, column=2, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(controls, text="SAVE TEMPLATE", fg_color="#333333", hover_color="#444444", command=self.template_save).grid(row=0, column=3, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(controls, text="RESET DEFAULT", fg_color="#333333", hover_color="#444444", command=self.template_reset_default).grid(row=0, column=4, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(
            controls,
            text="SET BACKGROUND FROM LIBRARY",
            fg_color="#333333",
            hover_color="#444444",
            command=self.template_set_background_from_selected
        ).grid(row=1, column=0, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(
            controls,
            text="BACKGROUND AUS DATEI",
            fg_color="#333333",
            hover_color="#444444",
            command=self.template_choose_background_file
        ).grid(row=1, column=1, padx=4, pady=4, sticky="ew")
        ctk.CTkButton(
            controls,
            text="CLEAR BACKGROUND",
            fg_color="#333333",
            hover_color="#444444",
            command=self.template_clear_background
        ).grid(row=1, column=2, columnspan=2, padx=4, pady=4, sticky="ew")


        layers = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        layers.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
        layers.grid_columnconfigure(0, weight=1)
        layers.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            layers,
            text="LAYERS",
            text_color=GOLD,
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

        self.template_layers_body = ctk.CTkScrollableFrame(layers, fg_color="#0B0B0B", corner_radius=12)
        self.template_layers_body.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))

        props = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        props.grid(row=0, column=3, sticky="nsew", padx=(12, 0))
        props.grid_columnconfigure(0, weight=1)
        props.grid_rowconfigure(1, weight=2)
        props.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(
            props,
            text="Properties",
            text_color=GOLD,
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

        self.template_props_body = ctk.CTkFrame(props, fg_color="#0B0B0B", corner_radius=12)
        self.template_props_body.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 10))
        self.template_props_body.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(
            props,
            text="Style Presets",
            text_color=GOLD,
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=2, column=0, padx=18, pady=(0, 6), sticky="w")

        style_box = ctk.CTkFrame(props, fg_color="#0B0B0B", corner_radius=12)
        style_box.grid(row=3, column=0, sticky="nsew", padx=18, pady=(0, 18))
        style_box.grid_columnconfigure(0, weight=1)
        style_box.grid_rowconfigure(1, weight=1)

        ctk.CTkButton(
            style_box,
            text="+ SAVE STYLE",
            fg_color=GOLD,
            text_color="#111111",
            hover_color=GOLD_DARK,
            command=self.template_save_style_preset
        ).grid(row=0, column=0, padx=10, pady=(10, 8), sticky="ew")

        self.template_styles_body = ctk.CTkScrollableFrame(style_box, fg_color="#080808", corner_radius=10)
        self.template_styles_body.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.template_build_properties_panel()
        self.template_ensure_field_ids()


        zoom_bar = ctk.CTkFrame(controls, fg_color="transparent")
        zoom_bar.grid(row=2, column=0, columnspan=5, padx=4, pady=(8, 0), sticky="ew")
        zoom_bar.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(zoom_bar, text="ZOOM -", fg_color="#333333", hover_color="#444444", command=self.template_zoom_out).grid(row=0, column=0, padx=(0, 4), sticky="ew")
        ctk.CTkLabel(zoom_bar, textvariable=self.template_zoom_label_var, text_color=GOLD, font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=1, padx=4, sticky="ew")
        ctk.CTkButton(zoom_bar, text="ZOOM +", fg_color="#333333", hover_color="#444444", command=self.template_zoom_in).grid(row=0, column=2, padx=4, sticky="ew")
        ctk.CTkButton(zoom_bar, text="100%", fg_color="#333333", hover_color="#444444", command=self.template_zoom_reset).grid(row=0, column=3, padx=4, sticky="ew")
        ctk.CTkButton(zoom_bar, text="PAN RESET", fg_color="#333333", hover_color="#444444", command=self.template_pan_reset).grid(row=0, column=4, padx=(4, 0), sticky="ew")

        smart_bar = ctk.CTkFrame(controls, fg_color="transparent")
        smart_bar.grid(row=3, column=0, columnspan=5, padx=4, pady=(6, 0), sticky="ew")
        smart_bar.grid_columnconfigure(2, weight=1)

        ctk.CTkCheckBox(
            smart_bar,
            text="SMART GUIDES",
            variable=self.template_smart_guides_enabled,
            command=self.template_smart_guides_changed,
            text_color="#BCA870",
            fg_color=GOLD,
            hover_color=GOLD_DARK
        ).grid(row=0, column=0, padx=(0, 12), sticky="w")

        ctk.CTkCheckBox(
            smart_bar,
            text="SMART SNAP",
            variable=self.template_smart_snap_enabled,
            command=self.template_smart_guides_changed,
            text_color="#BCA870",
            fg_color=GOLD,
            hover_color=GOLD_DARK
        ).grid(row=0, column=1, padx=(0, 12), sticky="w")

        align_bar = ctk.CTkFrame(controls, fg_color="transparent")
        align_bar.grid(row=4, column=0, columnspan=5, padx=4, pady=(6, 0), sticky="ew")
        align_bar.grid_columnconfigure((0,1,2,3,4,5), weight=1)

        ctk.CTkButton(align_bar, text="ALIGN LEFT", fg_color="#333333", hover_color="#444444", command=lambda: self.template_align_selected("left")).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(align_bar, text="CENTER", fg_color="#333333", hover_color="#444444", command=lambda: self.template_align_selected("center")).grid(row=0, column=1, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(align_bar, text="ALIGN RIGHT", fg_color="#333333", hover_color="#444444", command=lambda: self.template_align_selected("right")).grid(row=0, column=2, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(align_bar, text="ALIGN TOP", fg_color="#333333", hover_color="#444444", command=lambda: self.template_align_selected("top")).grid(row=0, column=3, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(align_bar, text="MIDDLE", fg_color="#333333", hover_color="#444444", command=lambda: self.template_align_selected("middle")).grid(row=0, column=4, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(align_bar, text="ALIGN BOTTOM", fg_color="#333333", hover_color="#444444", command=lambda: self.template_align_selected("bottom")).grid(row=0, column=5, padx=2, pady=2, sticky="ew")

        distribute_bar = ctk.CTkFrame(controls, fg_color="transparent")
        distribute_bar.grid(row=5, column=0, columnspan=5, padx=4, pady=(2, 0), sticky="ew")
        distribute_bar.grid_columnconfigure((0,1), weight=1)
        ctk.CTkButton(distribute_bar, text="DISTRIBUTE H", fg_color="#333333", hover_color="#444444", command=lambda: self.template_distribute_selected("horizontal")).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(distribute_bar, text="DISTRIBUTE V", fg_color="#333333", hover_color="#444444", command=lambda: self.template_distribute_selected("vertical")).grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        equal_bar = ctk.CTkFrame(controls, fg_color="transparent")
        equal_bar.grid(row=6, column=0, columnspan=5, padx=4, pady=(2, 0), sticky="ew")
        equal_bar.grid_columnconfigure((0,1), weight=1)
        ctk.CTkButton(equal_bar, text="EQUAL SPACE H", fg_color="#333333", hover_color="#444444", command=lambda: self.template_equal_spacing_selected("horizontal")).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(equal_bar, text="EQUAL SPACE V", fg_color="#333333", hover_color="#444444", command=lambda: self.template_equal_spacing_selected("vertical")).grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        history_bar = ctk.CTkFrame(controls, fg_color="transparent")
        history_bar.grid(row=7, column=0, columnspan=5, padx=4, pady=(2, 0), sticky="ew")
        history_bar.grid_columnconfigure((0,1), weight=1)
        ctk.CTkButton(history_bar, text="UNDO", fg_color="#333333", hover_color="#444444", command=self.template_undo).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(history_bar, text="REDO", fg_color="#333333", hover_color="#444444", command=self.template_redo).grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        group_bar = ctk.CTkFrame(controls, fg_color="transparent")
        group_bar.grid(row=8, column=0, columnspan=5, padx=4, pady=(2, 0), sticky="ew")
        group_bar.grid_columnconfigure((0,1), weight=1)
        ctk.CTkButton(group_bar, text="GROUP SELECTED", fg_color="#333333", hover_color="#444444", command=self.template_create_group).grid(row=0, column=0, padx=2, pady=2, sticky="ew")
        ctk.CTkButton(group_bar, text="UNGROUP", fg_color="#333333", hover_color="#444444", command=self.template_ungroup_selected).grid(row=0, column=1, padx=2, pady=2, sticky="ew")

        self.template_draw_canvas()
        self.template_build_style_presets_panel()
        self.template_build_layers_panel()

    def template_build_properties_panel(self):
        if not hasattr(self, "template_props_body"):
            return
        body = self.template_props_body
        for w in body.winfo_children():
            w.destroy()

        if self.template_selected_field is None:
            ctk.CTkLabel(
                body,
                text="Kein Feld ausgewählt.",
                text_color="#BCA870",
                wraplength=220,
                justify="left"
            ).grid(row=0, column=0, columnspan=2, padx=12, pady=12, sticky="w")
            return

        fields = [
            ("Name", self.template_prop_name),
            ("Font", self.template_prop_font_family),
            ("Size", self.template_prop_font_size),
            ("Text Color", self.template_prop_text_color),
            ("Stroke Color", self.template_prop_stroke_color),
            ("Stroke Width", self.template_prop_stroke_width),
        ]

        for row, (label, var) in enumerate(fields):
            ctk.CTkLabel(body, text=label, text_color="#BCA870").grid(row=row, column=0, padx=(12, 8), pady=6, sticky="w")
            entry = ctk.CTkEntry(body, textvariable=var)
            entry.grid(row=row, column=1, padx=(0, 12), pady=6, sticky="ew")
            if label == "Name":
                self.template_prop_name_entry = entry
            entry.bind("<KeyRelease>", lambda e: self.template_apply_selected_properties())

        ctk.CTkCheckBox(
            body,
            text="Uppercase",
            variable=self.template_prop_uppercase,
            text_color=TEXT,
            command=self.template_apply_selected_properties
        ).grid(row=len(fields), column=0, columnspan=2, padx=12, pady=8, sticky="w")

        ctk.CTkLabel(
            body,
            text="Änderungen werden automatisch gespeichert.",
            text_color="#D9C58C",
            wraplength=220,
            justify="left"
        ).grid(row=len(fields)+1, column=0, columnspan=2, padx=12, pady=(8, 12), sticky="w")



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
        self.template_collapsed_groups = set()
        self.template_selected_name = name
        self.template_selected_field = None
        self.template_selected_fields = set()
        self.template_working_data = load_template(name)
        self.show_template_editor_page()




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


    def template_draw_canvas(self):
        if not hasattr(self, "template_canvas"):
            return

        # Use in-memory working data while editing, otherwise click/drag would reset the fields.
        template = self.template_current()

        canvas = self.template_canvas
        canvas.delete("all")
        canvas.update_idletasks()

        cw = max(600, canvas.winfo_width())
        ch = max(360, canvas.winfo_height())

        bg_path = str(background_path(self.template_selected_name, template))
        bg_info = image_status(bg_path)

        self.template_bg_photo = None
        self.template_canvas_design_size = (1280, 720)

        if bg_path and bg_info["exists"]:
            try:
                original = load_rgba(bg_path)
                self.template_canvas_design_size = original.size
                _display, base_scale, _offset = fit_image_to_box(original, cw, ch, padding=40)
                scale = base_scale * float(getattr(self, "template_zoom_factor", 1.0))
                display = original.resize((max(1, int(original.size[0] * scale)), max(1, int(original.size[1] * scale))))
                base_offset = ((cw - display.size[0]) // 2, (ch - display.size[1]) // 2)
                offset = (
                    base_offset[0] + int(getattr(self, "template_pan_x", 0)),
                    base_offset[1] + int(getattr(self, "template_pan_y", 0))
                )
                self.template_canvas_scale = scale
                self.template_canvas_offset = offset
                self.template_bg_photo = tk.PhotoImage(data=pil_to_tk_photo_data(display))
                canvas.create_image(offset[0], offset[1], image=self.template_bg_photo, anchor="nw", tags="background")
                canvas.create_rectangle(offset[0], offset[1], offset[0] + display.size[0], offset[1] + display.size[1], outline="#3A2A0D", width=2)
            except Exception as e:
                self.template_canvas_scale = min((cw - 40) / 1280, (ch - 40) / 720) * float(getattr(self, 'template_zoom_factor', 1.0))
                self.template_canvas_offset = (((cw - int(1280 * self.template_canvas_scale)) // 2) + int(getattr(self, 'template_pan_x', 0)), ((ch - int(720 * self.template_canvas_scale)) // 2) + int(getattr(self, 'template_pan_y', 0)))
                ox, oy = self.template_canvas_offset
                dw, dh = int(1280 * self.template_canvas_scale), int(720 * self.template_canvas_scale)
                canvas.create_rectangle(ox, oy, ox + dw, oy + dh, fill="#111111", outline="#3A2A0D", width=2)
                canvas.create_text(ox + 20, oy + 20, text=f"Background Fehler:\n{e}", anchor="nw", fill="#D86A6A", font=("Arial", 14, "bold"))
        else:
            self.template_canvas_scale = min((cw - 40) / 1280, (ch - 40) / 720) * float(getattr(self, 'template_zoom_factor', 1.0))
            self.template_canvas_offset = (((cw - int(1280 * self.template_canvas_scale)) // 2) + int(getattr(self, 'template_pan_x', 0)), ((ch - int(720 * self.template_canvas_scale)) // 2) + int(getattr(self, 'template_pan_y', 0)))
            ox, oy = self.template_canvas_offset
            dw, dh = int(1280 * self.template_canvas_scale), int(720 * self.template_canvas_scale)
            canvas.create_rectangle(ox, oy, ox + dw, oy + dh, fill="#111111", outline="#3A2A0D", width=2)

        ox, oy = self.template_canvas_offset
        status_text = (
            f"Background: {bg_info['name']}\n"
            f"Status: {'✔ Datei gefunden' if bg_info['exists'] else '✖ kein/fehlender Hintergrund'}\n"
            f"Größe: {bg_info['size'] or '-'}"
        )
        canvas.create_text(ox + 18, oy + 18, text=status_text, anchor="nw", fill="#D6A43A", font=("Arial", 12, "bold"))

        self.template_update_fields_overlay(bg_info)


    def template_clear_fields_overlay(self):
        if not hasattr(self, "template_canvas"):
            return
        try:
            self.template_canvas.delete("template_overlay")
        except Exception:
            pass


    def template_clear_smart_guides(self):
        if hasattr(self, "template_canvas"):
            try:
                self.template_canvas.delete("template_smart_guide")
            except Exception:
                pass

    def template_screen_line_x(self, x):
        ox, _oy = getattr(self, "template_canvas_offset", (0, 0))
        scale = getattr(self, "template_canvas_scale", 1.0)
        return ox + int(x * scale)

    def template_screen_line_y(self, y):
        _ox, oy = getattr(self, "template_canvas_offset", (0, 0))
        scale = getattr(self, "template_canvas_scale", 1.0)
        return oy + int(y * scale)

    def template_field_edges(self, field):
        x = int(field.get("x", 0))
        y = int(field.get("y", 0))
        w = int(field.get("width", 0))
        h = int(field.get("height", 0))
        return {
            "left": x,
            "center_x": x + w // 2,
            "right": x + w,
            "top": y,
            "center_y": y + h // 2,
            "bottom": y + h,
        }

    def template_smart_targets(self):
        template = self.template_current()
        design_w, design_h = getattr(self, "template_canvas_design_size", (1280, 720))

        targets_x = [
            ("template_left", 0),
            ("template_center_x", design_w // 2),
            ("template_right", design_w),
        ]
        targets_y = [
            ("template_top", 0),
            ("template_center_y", design_h // 2),
            ("template_bottom", design_h),
        ]

        for idx, field in enumerate(template.get("fields", [])):
            if idx == self.template_selected_field or field.get("hidden", False):
                continue
            edges = self.template_field_edges(field)
            targets_x.extend([
                (f"field{idx}_left", edges["left"]),
                (f"field{idx}_center_x", edges["center_x"]),
                (f"field{idx}_right", edges["right"]),
            ])
            targets_y.extend([
                (f"field{idx}_top", edges["top"]),
                (f"field{idx}_center_y", edges["center_y"]),
                (f"field{idx}_bottom", edges["bottom"]),
            ])

        return targets_x, targets_y

    def template_draw_smart_guides(self, guides_x=None, guides_y=None):
        if not hasattr(self, "template_canvas"):
            return
        canvas = self.template_canvas
        canvas.delete("template_smart_guide")

        if not (getattr(self, "template_smart_guides_enabled", None) and self.template_smart_guides_enabled.get()):
            return

        guides_x = guides_x or []
        guides_y = guides_y or []

        design_w, design_h = getattr(self, "template_canvas_design_size", (1280, 720))
        ox, oy = getattr(self, "template_canvas_offset", (0, 0))
        scale = getattr(self, "template_canvas_scale", 1.0)
        x_min = ox
        x_max = ox + int(design_w * scale)
        y_min = oy
        y_max = oy + int(design_h * scale)

        for x in guides_x:
            sx = self.template_screen_line_x(x)
            canvas.create_line(
                sx, y_min, sx, y_max,
                fill=GOLD,
                width=2,
                dash=(6, 4),
                tags=("template_smart_guide",)
            )

        for y in guides_y:
            sy = self.template_screen_line_y(y)
            canvas.create_line(
                x_min, sy, x_max, sy,
                fill=GOLD,
                width=2,
                dash=(6, 4),
                tags=("template_smart_guide",)
            )

        try:
            canvas.tag_raise("template_smart_guide")
        except Exception:
            pass

    def template_apply_smart_snap(self, x, y, w, h, mode):
        """
        Returns x, y, w, h and active guide lines.
        Smart snap uses design coordinates, so it works correctly with zoom and pan.
        """
        if not (getattr(self, "template_smart_snap_enabled", None) and self.template_smart_snap_enabled.get()):
            return x, y, w, h, [], []

        tolerance = int(getattr(self, "template_smart_guide_tolerance", 8))
        targets_x, targets_y = self.template_smart_targets()

        moving = (mode or "move") == "move"
        guides_x = []
        guides_y = []

        def nearest_delta(values, targets):
            best = None
            for _name, target in targets:
                for value in values:
                    delta = target - value
                    if abs(delta) <= tolerance and (best is None or abs(delta) < abs(best[0])):
                        best = (delta, target)
            return best

        if moving:
            edges = {
                "left": x,
                "center_x": x + w // 2,
                "right": x + w,
                "top": y,
                "center_y": y + h // 2,
                "bottom": y + h,
            }

            snap_x = nearest_delta([edges["left"], edges["center_x"], edges["right"]], targets_x)
            if snap_x:
                x += snap_x[0]
                guides_x.append(snap_x[1])

            snap_y = nearest_delta([edges["top"], edges["center_y"], edges["bottom"]], targets_y)
            if snap_y:
                y += snap_y[0]
                guides_y.append(snap_y[1])

        else:
            # Resize snapping: snap only the actively moved edge(s).
            if "w" in mode:
                snap = nearest_delta([x], targets_x)
                if snap:
                    old_right = x + w
                    x = snap[1]
                    w = old_right - x
                    guides_x.append(snap[1])
            if "e" in mode:
                snap = nearest_delta([x + w], targets_x)
                if snap:
                    w = snap[1] - x
                    guides_x.append(snap[1])
            if "n" in mode:
                snap = nearest_delta([y], targets_y)
                if snap:
                    old_bottom = y + h
                    y = snap[1]
                    h = old_bottom - y
                    guides_y.append(snap[1])
            if "s" in mode:
                snap = nearest_delta([y + h], targets_y)
                if snap:
                    h = snap[1] - y
                    guides_y.append(snap[1])

        return x, y, w, h, guides_x, guides_y

    def template_smart_guides_changed(self):
        self.template_clear_smart_guides()



    def template_sync_selection_set(self):
        if not hasattr(self, "template_selected_fields"):
            self.template_selected_fields = set()
        if self.template_selected_field is None:
            if len(self.template_selected_fields) == 1:
                self.template_selected_field = next(iter(self.template_selected_fields))
            return
        self.template_selected_fields.add(self.template_selected_field)

    def template_selection_count(self):
        if not hasattr(self, "template_selected_fields"):
            self.template_selected_fields = set()
        return len(self.template_selected_fields)

    def template_clear_selection(self):
        self.template_selected_field = None
        self.template_selected_fields = set()

    def template_set_single_selection(self, idx):
        self.template_selected_field = idx
        self.template_selected_fields = {idx} if idx is not None else set()

    def template_toggle_selection(self, idx):
        if not hasattr(self, "template_selected_fields"):
            self.template_selected_fields = set()
        if idx in self.template_selected_fields:
            self.template_selected_fields.remove(idx)
            if self.template_selected_field == idx:
                self.template_selected_field = next(iter(self.template_selected_fields), None)
        else:
            self.template_selected_fields.add(idx)
            self.template_selected_field = idx


    def template_update_fields_overlay(self, bg_info=None):
        if not hasattr(self, "template_canvas"):
            return
        canvas = self.template_canvas
        self.template_clear_fields_overlay()
        self.template_clear_smart_guides()
        template = self.template_current()

        if bg_info is None:
            try:
                bg_path = str(background_path(self.template_selected_name, template))
                bg_info = image_status(bg_path)
            except Exception:
                bg_info = {"name": "?", "exists": False}

        for idx, field in enumerate(template.get("fields", [])):
            if field.get("hidden", False):
                continue
            x1, y1, x2, y2 = self.template_field_screen_rect(field)
            selected = idx == self.template_selected_field or idx in getattr(self, 'template_selected_fields', set())
            outline = GOLD if selected else "#BCA870"
            width = 3 if selected else 2

            canvas.create_rectangle(
                x1, y1, x2, y2,
                fill="#D6A43A",
                stipple="gray25",
                outline=outline,
                width=width,
                tags=("template_overlay",)
            )

            label_text = field.get("name", f"field_{idx+1}")
            if field.get("uppercase", True):
                label_text = label_text.upper()

            canvas.create_text(
                (x1 + x2) // 2,
                (y1 + y2) // 2,
                text=label_text,
                fill=field.get("text_color", "#FFFFFF"),
                font=("Arial", max(10, min(28, int(field.get("font_size", 90) / 5))), "bold"),
                tags=("template_overlay",)
            )

            canvas.create_text(
                x1 + 5, y1 + 5,
                text=field.get("name", f"field_{idx+1}"),
                anchor="nw",
                fill="#111111",
                font=("Arial", 9, "bold"),
                tags=("template_overlay",)
            )

            if selected:
                for _name, hx, hy in self.template_handle_points(x1, y1, x2, y2):
                    canvas.create_rectangle(
                        hx - 6, hy - 6, hx + 6, hy + 6,
                        fill=GOLD,
                        outline="#111111",
                        tags=("template_overlay",)
                    )

        if hasattr(self, "template_status_label"):
            selected_count = len(getattr(self, "template_selected_fields", set()))
            if selected_count > 1:
                self.template_status_label.configure(
                    text=f"{self.template_selected_name} | {selected_count} Felder ausgewählt | BG: {bg_info.get('name', '?')}",
                    text_color="#8FE6A0"
                )
            elif self.template_selected_field is not None and 0 <= self.template_selected_field < len(template.get("fields", [])):
                f = template["fields"][self.template_selected_field]
                self.template_status_label.configure(
                    text=f"{self.template_selected_name} | {f['name']} | {f['width']}×{f['height']} @ {f['x']}/{f['y']} | BG: {bg_info.get('name', '?')}",
                    text_color="#8FE6A0"
                )
            else:
                self.template_status_label.configure(
                    text=f"{self.template_selected_name} | Felder: {len(template.get('fields', []))} | BG: {bg_info.get('name', '?')}",
                    text_color="#8FE6A0"
                )

        if hasattr(self, "template_layers_body"):
            self.template_build_layers_panel()



    def template_field_screen_rect(self, field):
        ox, oy = self.template_canvas_offset
        s = self.template_canvas_scale
        x1 = ox + int(field["x"] * s)
        y1 = oy + int(field["y"] * s)
        x2 = ox + int((field["x"] + field["width"]) * s)
        y2 = oy + int((field["y"] + field["height"]) * s)
        return x1, y1, x2, y2

    def template_handle_points(self, x1, y1, x2, y2):
        return [
            ("nw", x1, y1),
            ("n", (x1+x2)//2, y1),
            ("ne", x2, y1),
            ("w", x1, (y1+y2)//2),
            ("e", x2, (y1+y2)//2),
            ("sw", x1, y2),
            ("s", (x1+x2)//2, y2),
            ("se", x2, y2),
        ]

    def template_draw_handles(self, canvas, x1, y1, x2, y2):
        for _name, hx, hy in self.template_handle_points(x1, y1, x2, y2):
            canvas.create_rectangle(
                hx - 6, hy - 6, hx + 6, hy + 6,
                fill=GOLD,
                outline="#111111"
            )

    def template_hit_test(self, x, y):
        template = self.template_current()
        tol = 10

        # selected field handles first
        if self.template_selected_field is not None and 0 <= self.template_selected_field < len(template["fields"]):
            f = template["fields"][self.template_selected_field]
            x1, y1, x2, y2 = self.template_field_screen_rect(f)
            for name, hx, hy in self.template_handle_points(x1, y1, x2, y2):
                if abs(x - hx) <= tol and abs(y - hy) <= tol:
                    return self.template_selected_field, name

            near_left = abs(x - x1) <= tol and y1 <= y <= y2
            near_right = abs(x - x2) <= tol and y1 <= y <= y2
            near_top = abs(y - y1) <= tol and x1 <= x <= x2
            near_bottom = abs(y - y2) <= tol and x1 <= x <= x2
            if near_left:
                return self.template_selected_field, "w"
            if near_right:
                return self.template_selected_field, "e"
            if near_top:
                return self.template_selected_field, "n"
            if near_bottom:
                return self.template_selected_field, "s"

        # any field body
        for idx in reversed(range(len(template["fields"]))):
            f = template["fields"][idx]
            if f.get("hidden", False):
                continue
            x1, y1, x2, y2 = self.template_field_screen_rect(f)
            if x1 <= x <= x2 and y1 <= y <= y2:
                return idx, "move"
        return None, None

    def template_cursor_for_mode(self, mode):
        if mode == "move":
            return "fleur"
        if mode in ("nw", "se"):
            return "size_nw_se"
        if mode in ("ne", "sw"):
            return "size_ne_sw"
        if mode in ("n", "s"):
            return "sb_v_double_arrow"
        if mode in ("e", "w"):
            return "sb_h_double_arrow"
        return "crosshair"

    def template_mouse_motion(self, event):
        _idx, mode = self.template_hit_test(event.x, event.y)
        self.template_canvas.configure(cursor=self.template_cursor_for_mode(mode))


    def template_marquee_clear(self):
        if hasattr(self, "template_canvas") and getattr(self, "template_marquee_item", None):
            try:
                self.template_canvas.delete(self.template_marquee_item)
            except Exception:
                pass
        self.template_marquee_item = None

    def template_marquee_start_select(self, event, add_mode=False):
        self.template_marquee_clear()
        self.template_marquee_active = True
        self.template_marquee_start = (event.x, event.y)
        self.template_marquee_add_mode = bool(add_mode)
        self.template_drag_mode = None
        self.template_drag_start = None
        self.template_drag_original = None
        self.template_group_drag_originals = None

        if hasattr(self, "template_canvas"):
            self.template_marquee_item = self.template_canvas.create_rectangle(
                event.x, event.y, event.x, event.y,
                outline=GOLD,
                width=2,
                dash=(6, 4),
                fill="#D6A43A",
                stipple="gray25",
                tags=("template_marquee",)
            )
            try:
                self.template_canvas.tag_raise("template_marquee")
            except Exception:
                pass

    def template_marquee_drag(self, event):
        if not getattr(self, "template_marquee_active", False):
            return False
        if not self.template_marquee_start:
            return True

        x0, y0 = self.template_marquee_start
        x1, y1 = event.x, event.y
        if hasattr(self, "template_canvas") and getattr(self, "template_marquee_item", None):
            self.template_canvas.coords(self.template_marquee_item, x0, y0, x1, y1)
        return True

    def template_marquee_finish(self, event):
        if not getattr(self, "template_marquee_active", False):
            return False

        x0, y0 = self.template_marquee_start or (event.x, event.y)
        x1, y1 = event.x, event.y
        self.template_marquee_active = False

        min_x, max_x = sorted((x0, x1))
        min_y, max_y = sorted((y0, y1))
        moved = abs(max_x - min_x) >= 4 or abs(max_y - min_y) >= 4

        self.template_marquee_clear()

        if not moved:
            if not getattr(self, "template_marquee_add_mode", False):
                self.template_clear_selection()
                self.template_load_selected_properties()
                if hasattr(self, "template_props_body"):
                    self.template_build_properties_panel()
                self.template_update_fields_overlay()
            return True

        template = self.template_current()
        found = set()

        for idx, field in enumerate(template.get("fields", [])):
            if field.get("hidden", False):
                continue

            fx1, fy1, fx2, fy2 = self.template_field_screen_rect(field)

            # Select fields whose visible rectangle intersects the marquee rectangle.
            intersects = not (fx2 < min_x or fx1 > max_x or fy2 < min_y or fy1 > max_y)
            if intersects:
                found.add(idx)

        if getattr(self, "template_marquee_add_mode", False):
            selected = set(getattr(self, "template_selected_fields", set()))
            selected.update(found)
            self.template_selected_fields = selected
            if found:
                self.template_selected_field = next(iter(found))
        else:
            self.template_selected_fields = found
            self.template_selected_field = next(iter(found), None)

        self.template_load_selected_properties()
        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()
        self.template_update_fields_overlay()
        if hasattr(self, "template_layers_body"):
            self.template_build_layers_panel()

        return True


    def template_mouse_down(self, event):
        try:
            self.template_canvas.focus_set()
        except Exception:
            pass
        idx, mode = self.template_hit_test(event.x, event.y)
        multi_pressed = self.template_multi_select_modifier(event)

        if idx is None:
            # Empty canvas drag starts marquee selection.
            # Plain drag replaces selection. Ctrl/Cmd-like modifier drag adds to selection.
            self.template_marquee_start_select(event, add_mode=multi_pressed)
            return

        selected = set(getattr(self, "template_selected_fields", set()))

        if multi_pressed:
            # Ctrl/Shift + click toggles membership.
            self.template_toggle_selection(idx)
        else:
            # Important group-drag behavior:
            # If multiple fields are already selected and the user clicks one of them,
            # keep the whole selection. This allows dragging the group.
            if idx in selected and len(selected) > 1:
                self.template_selected_field = idx
            else:
                self.template_set_single_selection(idx)

        self.template_load_selected_properties()
        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()

        if self.template_is_field_locked(idx):
            self.template_drag_mode = None
            self.template_drag_start = None
            self.template_drag_original = None
            self.template_group_drag_originals = None
            self.template_update_fields_overlay()
            return

        self.template_drag_history_snapshot = self.template_snapshot()
        self.template_drag_mode = mode
        self.template_drag_start = (event.x, event.y)
        template = self.template_current()
        self.template_drag_original = dict(template["fields"][idx])

        selected = set(getattr(self, "template_selected_fields", set()))
        if idx in selected and len(selected) > 1 and mode == "move":
            self.template_group_drag_originals = {
                i: dict(template["fields"][i])
                for i in selected
                if 0 <= i < len(template.get("fields", [])) and not self.template_is_field_locked(i)
            }
            if not self.template_group_drag_originals:
                self.template_group_drag_originals = None
        else:
            self.template_group_drag_originals = None

        self.template_update_fields_overlay()


    def template_mouse_drag(self, event):
        if self.template_marquee_drag(event):
            return
        if self.template_selected_field is None or self.template_drag_original is None:
            return

        template = self.template_current()
        sx, sy = self.template_drag_start
        dx = int((event.x - sx) / self.template_canvas_scale)
        dy = int((event.y - sy) / self.template_canvas_scale)

        # Group move: if multiple fields are selected and one selected field is dragged,
        # move all selected fields together. Resizing remains single-field for now.
        group_originals = getattr(self, "template_group_drag_originals", None)
        if group_originals and (self.template_drag_mode or "move") == "move":
            design_w, design_h = getattr(self, "template_canvas_design_size", (1280, 720))

            # Keep the entire group inside the template bounds.
            min_dx = max(-int(f.get("x", 0)) for f in group_originals.values())
            min_dy = max(-int(f.get("y", 0)) for f in group_originals.values())
            max_dx = min(design_w - (int(f.get("x", 0)) + int(f.get("width", 0))) for f in group_originals.values())
            max_dy = min(design_h - (int(f.get("y", 0)) + int(f.get("height", 0))) for f in group_originals.values())
            dx = max(min_dx, min(max_dx, dx))
            dy = max(min_dy, min(max_dy, dy))

            template = self.template_current()
            for idx, original in group_originals.items():
                f = dict(original)
                f["x"] = int(f.get("x", 0)) + dx
                f["y"] = int(f.get("y", 0)) + dy
                template["fields"][idx] = f

            self.template_update_fields_overlay()
            return

        f = dict(self.template_drag_original)
        x, y, w, h = f["x"], f["y"], f["width"], f["height"]
        mode = self.template_drag_mode or "move"

        if mode == "move":
            x += dx
            y += dy
        else:
            if "w" in mode:
                x += dx
                w -= dx
            if "e" in mode:
                w += dx
            if "n" in mode:
                y += dy
                h -= dy
            if "s" in mode:
                h += dy

        if w < 0:
            x += w
            w = abs(w)
        if h < 0:
            y += h
            h = abs(h)

        min_w, min_h = 40, 30
        design_w, design_h = getattr(self, "template_canvas_design_size", (1280, 720))
        x = max(0, min(design_w - min_w, x))
        y = max(0, min(design_h - min_h, y))
        w = max(min_w, min(design_w - x, w))
        h = max(min_h, min(design_h - y, h))

        # Smart Guides / Smart Snap before final constraints.
        x, y, w, h, guides_x, guides_y = self.template_apply_smart_snap(x, y, w, h, mode)

        min_w, min_h = 40, 30
        design_w, design_h = getattr(self, "template_canvas_design_size", (1280, 720))
        x = max(0, min(design_w - min_w, x))
        y = max(0, min(design_h - min_h, y))
        w = max(min_w, min(design_w - x, w))
        h = max(min_h, min(design_h - y, h))

        f["x"], f["y"], f["width"], f["height"] = int(x), int(y), int(w), int(h)
        template["fields"][self.template_selected_field] = f
        self.template_update_fields_overlay()
        self.template_draw_smart_guides(guides_x, guides_y)


    def template_mouse_up(self, event):
        if self.template_marquee_finish(event):
            return
        self.template_clear_smart_guides()
        if getattr(self, "template_drag_history_snapshot", None) is not None:
            current = self.template_current()
            if current != self.template_drag_history_snapshot:
                self.template_undo_stack.append(self.template_drag_history_snapshot)
                limit = int(getattr(self, "template_history_limit", 80))
                if len(self.template_undo_stack) > limit:
                    self.template_undo_stack = self.template_undo_stack[-limit:]
                self.template_redo_stack.clear()
            self.template_drag_history_snapshot = None
        save_template(self.template_selected_name, self.template_current())
        self.template_drag_mode = None
        self.template_drag_start = None
        self.template_drag_original = None
        self.template_group_drag_originals = None



    def card_template_safe_name(self):
        return "".join(c if c.isalnum() or c in "-_" else "_" for c in self.card_selected_template.get())

    def card_default_output_name(self):
        return f"card_{self.card_template_safe_name()}"

    def card_output_path(self, final=False):
        base = self.card_output_name.get().strip() if hasattr(self, "card_output_name") else ""
        if not base:
            base = self.card_default_output_name()
        profile = self.card_export_profile.get() if hasattr(self, "card_export_profile") else "Broadcast PNG"
        return export_engine.export_path(EXPORT_DIR, base, profile, final=final)

    def card_preview_changed(self):
        self.card_save_values()
        if getattr(self, "card_auto_preview", None) is None or self.card_auto_preview.get():
            self.card_update_preview()

    def card_clear_values(self):
        self.card_push_data_history()
        values = self.card_creator_values.get(self.card_selected_template.get(), {})
        for var in values.values():
            if hasattr(var, "set"):
                var.set("")
        self.card_save_values()
        self.card_update_preview()

    def card_open_export_folder(self):
        try:
            EXPORT_DIR.mkdir(parents=True, exist_ok=True)
            os.startfile(str(EXPORT_DIR))
        except Exception as e:
            messagebox.showerror("Card Creator", f"Export-Ordner konnte nicht geöffnet werden:\\n{e}")

    def card_copy_last_path(self):
        if not self.card_creator_last_render:
            messagebox.showinfo("Card Creator", "Noch keine finale Karte gerendert.")
            return
        try:
            self.clipboard_clear()
            self.clipboard_append(str(self.card_creator_last_render))
            messagebox.showinfo("Card Creator", "Pfad wurde in die Zwischenablage kopiert.")
        except Exception as e:
            messagebox.showerror("Card Creator", str(e))



    def card_current_data_snapshot(self):
        return dict(self.card_values_plain())

    def card_apply_data_snapshot(self, snapshot):
        values = self.card_creator_values.get(self.card_selected_template.get(), {})
        # Ensure variables exist by building form before applying if needed.
        for key, value in snapshot.items():
            if key in values and hasattr(values[key], "set"):
                values[key].set(value)

        # Keys not in snapshot should become empty.
        for key, var in values.items():
            if key not in snapshot and hasattr(var, "set"):
                var.set("")

        self.card_save_values()
        self.card_update_preview()

    def card_push_data_history(self):
        snapshot = self.card_current_data_snapshot()
        if self.card_data_undo_stack and self.card_data_undo_stack[-1] == snapshot:
            return
        self.card_data_undo_stack.append(snapshot)
        if len(self.card_data_undo_stack) > self.card_history_limit:
            self.card_data_undo_stack.pop(0)
        self.card_data_redo_stack.clear()

    def card_undo_data(self):
        if not self.card_data_undo_stack:
            messagebox.showinfo("Card Creator", "Nichts zum Rückgängig machen.")
            return
        current = self.card_current_data_snapshot()
        previous = self.card_data_undo_stack.pop()
        self.card_data_redo_stack.append(current)
        self.card_apply_data_snapshot(previous)

    def card_redo_data(self):
        if not self.card_data_redo_stack:
            messagebox.showinfo("Card Creator", "Nichts zum Wiederherstellen.")
            return
        current = self.card_current_data_snapshot()
        next_snapshot = self.card_data_redo_stack.pop()
        self.card_data_undo_stack.append(current)
        self.card_apply_data_snapshot(next_snapshot)



    def card_template_field_index_by_name(self, field_name):
        template = self.card_template()
        for idx, field in enumerate(template.get("fields", [])):
            if field.get("name") == field_name:
                return idx
        return None

    def card_apply_style_to_field(self, field_name, style_name):
        if not style_name or style_name == "Select Style":
            return

        template_name = self.card_selected_template.get()
        template = load_template(template_name)
        fields = template.get("fields", [])

        target_idx = None
        for idx, field in enumerate(fields):
            if field.get("name") == field_name:
                target_idx = idx
                break

        if target_idx is None:
            messagebox.showwarning("Card Creator Styles", f"Feld nicht gefunden: {field_name}")
            return

        try:
            if hasattr(self, "template_push_history"):
                # Only meaningful if the same template is open in the Template Editor later,
                # but it keeps the operation conceptually tracked.
                pass

            style = style_engine.load_style(style_name)
            if not style:
                messagebox.showwarning("Card Creator Styles", "Style ist leer oder konnte nicht geladen werden.")
                return

            style_engine.apply_style(fields[target_idx], style)
            save_template(template_name, template)

            # Keep working data in sync if this template is also active in Template Editor.
            if getattr(self, "template_selected_name", None) == template_name:
                self.template_working_data = None

            self.card_update_preview()
            messagebox.showinfo("Card Creator Styles", f"Style '{style_name}' wurde auf '{field_name}' angewendet.")
        except Exception as e:
            messagebox.showerror("Card Creator Styles", str(e))

    def card_open_template_editor_for_styles(self):
        self.template_selected_name = self.card_selected_template.get()
        self.show_template_editor_page()



    def card_batch_current_item_name(self):
        base = self.card_output_name.get().strip() if hasattr(self, "card_output_name") else ""
        if not base:
            base = self.card_default_output_name()
        return base

    def card_batch_add_current(self):
        try:
            self.card_save_values()
            item = {
                "template": self.card_selected_template.get(),
                "output_name": self.card_batch_current_item_name(),
                "profile": self.card_export_profile.get(),
                "values": dict(self.card_values_plain()),
            }
            self.card_batch_items.append(item)
            self.card_batch_selected_index = len(self.card_batch_items) - 1

            self.card_build_batch_panel()

            if hasattr(self, "card_render_status"):
                self.card_render_status.configure(
                    text=f"Batch: {len(self.card_batch_items)} Karte(n) in der Liste.",
                    text_color="#8FE6A0"
                )
        except Exception as e:
            messagebox.showerror("Batch Cards", f"Add Current fehlgeschlagen:\n{e}")

    def card_batch_duplicate_selected(self):
        idx = self.card_batch_selected_index
        if idx is None or not (0 <= idx < len(self.card_batch_items)):
            messagebox.showinfo("Batch Cards", "Bitte zuerst einen Batch-Eintrag auswählen.")
            return

        original = self.card_batch_items[idx]
        copy_item = {
            "template": original.get("template", ""),
            "output_name": str(original.get("output_name", "card")) + "_copy",
            "profile": original.get("profile", "Broadcast PNG"),
            "values": dict(original.get("values", {})),
        }
        self.card_batch_items.insert(idx + 1, copy_item)
        self.card_batch_selected_index = idx + 1
        self.card_build_batch_panel()

    def card_batch_remove_selected(self):
        idx = self.card_batch_selected_index
        if idx is None or not (0 <= idx < len(self.card_batch_items)):
            messagebox.showinfo("Batch Cards", "Bitte zuerst einen Batch-Eintrag auswählen.")
            return
        self.card_batch_items.pop(idx)
        self.card_batch_selected_index = None
        self.card_build_batch_panel()

    def card_batch_clear(self):
        if not self.card_batch_items:
            return
        if not messagebox.askyesno("Batch Cards", "Batch-Liste wirklich leeren?"):
            return
        self.card_batch_items.clear()
        self.card_batch_selected_index = None
        self.card_build_batch_panel()

    def card_batch_select(self, idx):
        if not (0 <= idx < len(self.card_batch_items)):
            return

        self.card_batch_selected_index = idx
        item = self.card_batch_items[idx]

        template_name = item.get("template", "")
        if template_name in list_templates():
            self.card_selected_template.set(template_name)

        self.card_output_name.set(item.get("output_name", self.card_default_output_name()))
        self.card_export_profile.set(item.get("profile", "Broadcast PNG"))

        # Rebuild form first so StringVars exist, then apply values.
        self.card_build_form()
        values = self.card_creator_values.get(self.card_selected_template.get(), {})
        for key, var in values.items():
            if hasattr(var, "set"):
                var.set(str(item.get("values", {}).get(key, "")))

        self.card_save_values()
        self.card_update_preview()
        self.card_build_batch_panel()

    def card_build_batch_panel(self):
        if not hasattr(self, "card_batch_body"):
            return

        for w in self.card_batch_body.winfo_children():
            w.destroy()

        if not self.card_batch_items:
            ctk.CTkLabel(
                self.card_batch_body,
                text="Noch keine Batch-Karten.\nKlicke + ADD CURRENT.",
                text_color="#777777",
                wraplength=240,
                justify="left"
            ).grid(row=0, column=0, padx=8, pady=8, sticky="w")
            return

        for row, item in enumerate(self.card_batch_items):
            active = row == self.card_batch_selected_index
            title = f"{row+1}. {item.get('output_name', 'card')}"
            subtitle = f"{item.get('template', '')} · {item.get('profile', '')}"

            row_box = ctk.CTkFrame(
                self.card_batch_body,
                fg_color=GOLD if active else "#171717",
                corner_radius=8
            )
            row_box.grid(row=row, column=0, padx=8, pady=4, sticky="ew")
            row_box.grid_columnconfigure(0, weight=1)

            title_label = ctk.CTkLabel(
                row_box,
                text=title,
                text_color="#111111" if active else "#D9C58C",
                anchor="w"
            )
            title_label.grid(row=0, column=0, padx=10, pady=(6, 0), sticky="ew")

            subtitle_label = ctk.CTkLabel(
                row_box,
                text=subtitle,
                text_color="#333333" if active else "#777777",
                anchor="w"
            )
            subtitle_label.grid(row=1, column=0, padx=10, pady=(0, 6), sticky="ew")

            for widget in (row_box, title_label, subtitle_label):
                widget.bind("<Button-1>", lambda _e, i=row: self.card_batch_select(i))

        self.card_batch_body.grid_columnconfigure(0, weight=1)


    def card_render_batch(self):
        if not self.card_batch_items:
            messagebox.showinfo("Batch Cards", "Batch-Liste ist leer.")
            return

        rendered = []
        old_template = self.card_selected_template.get()
        old_output = self.card_output_name.get()
        old_profile = self.card_export_profile.get()
        old_values_snapshot = self.card_values_plain()

        try:
            for item in self.card_batch_items:
                template_name = item.get("template", "")
                if template_name not in list_templates():
                    continue

                self.card_selected_template.set(template_name)
                self.card_output_name.set(item.get("output_name", self.card_default_output_name()))
                self.card_export_profile.set(item.get("profile", "Broadcast PNG"))

                if template_name not in self.card_creator_values:
                    self.card_creator_values[template_name] = {}
                # Ensure form variables exist for this template.
                self.card_build_form()
                values = self.card_creator_values.get(template_name, {})
                for key, var in values.items():
                    if hasattr(var, "set"):
                        var.set(str(item.get("values", {}).get(key, "")))

                out = self.card_render_to_file(final=True)
                rendered.append(str(out))

            self.card_render_status.configure(text=f"Batch gerendert: {len(rendered)} Datei(en)", text_color="#8FE6A0")
            messagebox.showinfo("Batch Cards", f"Batch gerendert:\\n{len(rendered)} Datei(en)")
        except Exception as e:
            messagebox.showerror("Batch Cards", str(e))
        finally:
            # Restore the user's previous UI state as much as possible.
            if old_template in list_templates():
                self.card_selected_template.set(old_template)
            self.card_output_name.set(old_output)
            self.card_export_profile.set(old_profile)
            self.card_build_form()
            values = self.card_creator_values.get(self.card_selected_template.get(), {})
            for key, var in values.items():
                if hasattr(var, "set"):
                    var.set(str(old_values_snapshot.get(key, "")))
            self.card_save_values()
            self.card_update_preview()
            self.card_build_batch_panel()



    def card_import_batch_file(self):
        from pathlib import Path as _Path

        selected_path = filedialog.askopenfilename(
            title="CSV oder Excel-Datei importieren",
            filetypes=[
                ("CSV / Excel", "*.csv *.xlsx"),
                ("CSV", "*.csv"),
                ("Excel", "*.xlsx"),
                ("Alle Dateien", "*.*"),
            ],
        )
        if not selected_path:
            return

        try:
            import_path = _Path(selected_path)
            rows = batch_engine.read_table(import_path)
            if not rows:
                messagebox.showinfo("Batch Import", "Die Datei enthält keine Datensätze.")
                return

            template = self.card_template()
            fields = template.get("fields", [])
            items = batch_engine.rows_to_batch_items(
                rows,
                self.card_selected_template.get(),
                fields,
                self.card_batch_current_item_name(),
                self.card_export_profile.get(),
            )

            matched = [item for item in items if item.get("values")]
            if not matched:
                field_names = ", ".join([f.get("name", "") for f in fields if f.get("name")])
                messagebox.showwarning(
                    "Batch Import",
                    "Keine passenden Spalten gefunden.\n\n"
                    f"Datei: {import_path.name}\n"
                    f"Template-Felder: {field_names}\n\n"
                    "Tipp: Die Spaltennamen müssen zu den Feldnamen im Template passen, z.B. date, game, time, feature."
                )
                return

            self.card_batch_items.extend(matched)
            self.card_batch_selected_index = len(self.card_batch_items) - len(matched)
            self.card_build_batch_panel()

            if hasattr(self, "card_render_status"):
                self.card_render_status.configure(
                    text=f"Batch Import: {len(matched)} Karte(n) hinzugefügt.",
                    text_color="#8FE6A0"
                )

            messagebox.showinfo("Batch Import", f"{len(matched)} Batch-Karte(n) importiert.\n\nDatei:\n{import_path}")
        except Exception as e:
            messagebox.showerror("Batch Import", f"Import fehlgeschlagen:\n{e}")



    def card_save_batch_project(self):
        try:
            if not self.card_batch_items:
                messagebox.showinfo("Batch Project", "Die Batch-Liste ist leer.")
                return

            initial_dir = str(batch_engine.batch_projects_dir())
            path = filedialog.asksaveasfilename(
                title="Batch Project speichern",
                initialdir=initial_dir,
                initialfile="new_batch_project.vbatch",
                defaultextension=".vbatch",
                filetypes=[
                    ("VADAFOK Batch Project", "*.vbatch"),
                    ("JSON", "*.json"),
                    ("Alle Dateien", "*.*"),
                ],
            )

            if not path:
                if hasattr(self, "card_render_status"):
                    self.card_render_status.configure(text="SAVE PROJECT abgebrochen.", text_color="#BCA870")
                return

            saved_path = batch_engine.save_batch_project_file(path, self.card_batch_items)

            if hasattr(self, "card_render_status"):
                self.card_render_status.configure(
                    text=f"Batch Project gespeichert.",
                    text_color="#8FE6A0"
                )

            messagebox.showinfo("Batch Project", f"Batch Project gespeichert:\n{saved_path}")
        except Exception as e:
            messagebox.showerror("Batch Project", f"SAVE PROJECT Fehler:\n{e}")

    def card_load_batch_project(self):
        try:
            initial_dir = str(batch_engine.batch_projects_dir())
            path = filedialog.askopenfilename(
                title="Batch Project laden",
                initialdir=initial_dir,
                filetypes=[
                    ("VADAFOK Batch Project", "*.vbatch"),
                    ("JSON", "*.json"),
                    ("Alle Dateien", "*.*"),
                ],
            )

            if not path:
                if hasattr(self, "card_render_status"):
                    self.card_render_status.configure(text="LOAD PROJECT abgebrochen.", text_color="#BCA870")
                return

            items = batch_engine.load_batch_project_file(path)
            self.card_batch_items = items
            self.card_batch_selected_index = 0 if items else None
            self.card_build_batch_panel()

            if items:
                self.card_batch_select(0)
            else:
                self.card_update_preview()

            if hasattr(self, "card_render_status"):
                self.card_render_status.configure(
                    text=f"Batch Project geladen: {len(items)} Karte(n)",
                    text_color="#8FE6A0"
                )

            messagebox.showinfo("Batch Project", f"Batch Project geladen:\n{len(items)} Karte(n)")
        except Exception as e:
            messagebox.showerror("Batch Project", f"LOAD PROJECT Fehler:\n{e}")


    def show_card_creator_page(self):
        self.set_active("Card Creator")
        self.clear_main()
        self.page_title("Card Creator")

        names = list_templates()
        if not names:
            create_template("Default Stream Plan")
            names = list_templates()

        if not self.card_selected_template.get() or self.card_selected_template.get() not in names:
            default_name = get_default_template()
            self.card_selected_template.set(default_name if default_name in names else sorted(names)[0])

        if not self.card_output_name.get():
            self.card_output_name.set(self.card_default_output_name())

        outer = ctk.CTkFrame(self.main, fg_color=DARK)
        outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_columnconfigure(1, weight=4)
        outer.grid_columnconfigure(2, weight=2)
        outer.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        left.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(left, text="Templates", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

        tlist = ctk.CTkScrollableFrame(left, fg_color="#0B0B0B", corner_radius=12)
        tlist.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        for name in sorted(list_templates()):
            prefix = "✓ " if name == self.card_selected_template.get() else ""
            ctk.CTkButton(
                tlist,
                text=prefix + name,
                anchor="w",
                fg_color="#171717",
                hover_color="#2C2C2C",
                command=lambda n=name: self.card_select_template(n)
            ).pack(fill="x", padx=8, pady=4)

        preview = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        preview.grid(row=0, column=1, sticky="nsew", padx=12)
        preview.grid_columnconfigure(0, weight=1)
        preview.grid_rowconfigure(2, weight=1)

        header = ctk.CTkFrame(preview, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))
        header.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(header, text="Preview", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, sticky="w")
        self.card_preview_info = ctk.CTkLabel(header, text="", text_color="#8FE6A0", anchor="e")
        self.card_preview_info.grid(row=0, column=1, sticky="e")

        preview_actions = ctk.CTkFrame(preview, fg_color="transparent")
        preview_actions.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 8))
        preview_actions.grid_columnconfigure((0, 1, 2, 3), weight=1)
        ctk.CTkButton(preview_actions, text="UPDATE PREVIEW", fg_color="#333333", hover_color="#444444", command=self.card_update_preview).grid(row=0, column=0, padx=(0, 4), sticky="ew")
        ctk.CTkButton(preview_actions, text="OPEN EXPORTS", fg_color="#333333", hover_color="#444444", command=self.card_open_export_folder).grid(row=0, column=1, padx=4, sticky="ew")
        ctk.CTkButton(preview_actions, text="REFRESH STYLES", fg_color="#333333", hover_color="#444444", command=self.card_build_form).grid(row=0, column=2, padx=4, sticky="ew")
        ctk.CTkButton(preview_actions, text="COPY LAST PATH", fg_color="#333333", hover_color="#444444", command=self.card_copy_last_path).grid(row=0, column=3, padx=(4, 0), sticky="ew")

        self.card_preview_frame = ctk.CTkFrame(preview, fg_color="#050505", corner_radius=14, border_color="#3A2A0D", border_width=1)
        self.card_preview_frame.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))

        form = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        form.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
        form.grid_columnconfigure(0, weight=1)
        form.grid_rowconfigure(1, weight=3)
        form.grid_rowconfigure(2, weight=2)

        ctk.CTkLabel(form, text="Card Data", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

        self.card_form_frame = ctk.CTkScrollableFrame(form, fg_color="#0B0B0B", corner_radius=12)
        self.card_form_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 12))
        self.card_form_frame.grid_columnconfigure(0, weight=1)

        batch_box = ctk.CTkFrame(form, fg_color="#0B0B0B", corner_radius=12)
        batch_box.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 12))
        batch_box.grid_columnconfigure(0, weight=1)
        batch_box.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(
            batch_box,
            text="Batch Cards",
            text_color=GOLD,
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, padx=10, pady=(10, 6), sticky="w")

        batch_actions = ctk.CTkFrame(batch_box, fg_color="transparent")
        batch_actions.grid(row=1, column=0, padx=10, pady=(0, 6), sticky="ew")
        batch_actions.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(batch_actions, text="+ ADD CURRENT", fg_color="#333333", hover_color="#444444", command=self.card_batch_add_current).grid(row=0, column=0, padx=(0, 4), pady=2, sticky="ew")
        ctk.CTkButton(batch_actions, text="RENDER BATCH", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=self.card_render_batch).grid(row=0, column=1, padx=(4, 0), pady=2, sticky="ew")
        ctk.CTkButton(batch_actions, text="IMPORT CSV/XLSX", fg_color="#333333", hover_color="#444444", command=self.card_import_batch_file).grid(row=1, column=0, columnspan=2, padx=0, pady=2, sticky="ew")
        ctk.CTkButton(batch_actions, text="SAVE PROJECT", fg_color="#333333", hover_color="#444444", command=self.card_save_batch_project).grid(row=2, column=0, padx=(0, 4), pady=2, sticky="ew")
        ctk.CTkButton(batch_actions, text="LOAD PROJECT", fg_color="#333333", hover_color="#444444", command=self.card_load_batch_project).grid(row=2, column=1, padx=(4, 0), pady=2, sticky="ew")
        ctk.CTkButton(batch_actions, text="DUPLICATE", fg_color="#333333", hover_color="#444444", command=self.card_batch_duplicate_selected).grid(row=3, column=0, padx=(0, 4), pady=2, sticky="ew")
        ctk.CTkButton(batch_actions, text="REMOVE", fg_color="#5A1F1F", hover_color="#7A2A2A", command=self.card_batch_remove_selected).grid(row=3, column=1, padx=(4, 0), pady=2, sticky="ew")

        self.card_batch_body = ctk.CTkScrollableFrame(batch_box, fg_color="#080808", corner_radius=10, height=190)
        self.card_batch_body.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

        export_box = ctk.CTkFrame(form, fg_color="#0B0B0B", corner_radius=12)
        export_box.grid(row=3, column=0, sticky="ew", padx=18, pady=(0, 12))
        export_box.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(export_box, text="Output Name", text_color="#BCA870").grid(row=0, column=0, padx=10, pady=(10, 2), sticky="w")
        ctk.CTkEntry(export_box, textvariable=self.card_output_name).grid(row=1, column=0, padx=10, pady=(0, 8), sticky="ew")

        ctk.CTkLabel(export_box, text="Export Profile", text_color="#BCA870").grid(row=2, column=0, padx=10, pady=(2, 2), sticky="w")
        ctk.CTkOptionMenu(
            export_box,
            values=export_engine.list_export_profiles(),
            variable=self.card_export_profile,
            fg_color="#333333",
            button_color="#444444",
            button_hover_color="#555555",
            command=lambda _v: self.card_update_preview()
        ).grid(row=3, column=0, padx=10, pady=(0, 8), sticky="ew")

        self.card_export_profile_info = ctk.CTkLabel(export_box, text="", text_color="#777777", wraplength=240, justify="left")
        self.card_export_profile_info.grid(row=4, column=0, padx=10, pady=(0, 8), sticky="w")

        ctk.CTkCheckBox(
            export_box,
            text="Auto Preview",
            variable=self.card_auto_preview,
            text_color="#BCA870",
            fg_color=GOLD,
            hover_color=GOLD_DARK
        ).grid(row=5, column=0, padx=10, pady=(0, 10), sticky="w")

        buttons = ctk.CTkFrame(form, fg_color="transparent")
        buttons.grid(row=4, column=0, sticky="ew", padx=18, pady=(0, 18))
        buttons.grid_columnconfigure((0, 1), weight=1)
        ctk.CTkButton(buttons, text="CLEAR FIELDS", fg_color="#333333", hover_color="#444444", command=self.card_clear_values).grid(row=0, column=0, padx=(0, 4), pady=4, sticky="ew")
        ctk.CTkButton(buttons, text="RENDER CARD", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=self.card_render_final).grid(row=0, column=1, padx=(4, 0), pady=4, sticky="ew")

        ctk.CTkButton(buttons, text="UNDO DATA", fg_color="#333333", hover_color="#444444", command=self.card_undo_data).grid(row=1, column=0, padx=(0, 4), pady=4, sticky="ew")
        ctk.CTkButton(buttons, text="REDO DATA", fg_color="#333333", hover_color="#444444", command=self.card_redo_data).grid(row=1, column=1, padx=(4, 0), pady=4, sticky="ew")

        self.card_render_status = ctk.CTkLabel(buttons, text="Noch nicht gerendert.", text_color="#BCA870", wraplength=260, justify="left")
        self.card_render_status.grid(row=2, column=0, columnspan=2, pady=(8, 0), sticky="w")

        self.card_build_form()
        self.card_build_batch_panel()
        self.card_update_preview()




    def card_select_template(self, name):
        self.card_selected_template.set(name)
        self.card_output_name.set(self.card_default_output_name())
        self.card_data_undo_stack = []
        self.card_data_redo_stack = []
        self.card_creator_preview_image = None
        self.card_creator_last_render = None
        self.show_card_creator_page()



    def card_template(self):
        names = list_templates()
        if not names:
            create_template("Default Stream Plan")
            names = list_templates()

        selected = self.card_selected_template.get()
        if selected not in names:
            default_name = get_default_template()
            selected = default_name if default_name in names else sorted(names)[0]
            self.card_selected_template.set(selected)

        return load_template(selected)


    def card_build_form(self):
        for w in self.card_form_frame.winfo_children():
            w.destroy()
        template = self.card_template()
        fields = template.get("fields", [])
        if self.card_selected_template.get() not in self.card_creator_values:
            self.card_creator_values[self.card_selected_template.get()] = {}
        values = self.card_creator_values[self.card_selected_template.get()]

        if not fields:
            ctk.CTkLabel(self.card_form_frame, text="Dieses Template hat keine Felder.", text_color="#BCA870").grid(row=0, column=0, padx=12, pady=12, sticky="w")
            return

        available_styles = style_engine.list_styles()
        style_options = ["Select Style"] + available_styles

        for row, field in enumerate(fields):
            name = field.get("name", f"field_{row+1}")
            saved = self.card_saved_values.get(self.card_selected_template.get(), {})
            if name not in values or not hasattr(values.get(name), "get"):
                values[name] = ctk.StringVar(value=str(saved.get(name, "")))

            label = name.replace("_", " ").title()

            field_box = ctk.CTkFrame(self.card_form_frame, fg_color="#111111", corner_radius=10)
            field_box.grid(row=row, column=0, padx=10, pady=(8, 4), sticky="ew")
            field_box.grid_columnconfigure(0, weight=1)

            ctk.CTkLabel(field_box, text=label, text_color="#BCA870").grid(row=0, column=0, padx=10, pady=(8, 2), sticky="w")

            entry = ctk.CTkEntry(field_box, textvariable=values[name])
            entry.grid(row=1, column=0, padx=10, pady=(0, 8), sticky="ew")
            entry.bind("<KeyRelease>", lambda e: self.card_preview_changed())

            style_row = ctk.CTkFrame(field_box, fg_color="transparent")
            style_row.grid(row=2, column=0, padx=10, pady=(0, 10), sticky="ew")
            style_row.grid_columnconfigure(0, weight=1)

            style_var = ctk.StringVar(value="Select Style")
            style_menu = ctk.CTkOptionMenu(
                style_row,
                values=style_options,
                variable=style_var,
                fg_color="#333333",
                button_color="#444444",
                button_hover_color="#555555",
                command=lambda selected, field_name=name: self.card_apply_style_to_field(field_name, selected)
            )
            style_menu.grid(row=0, column=0, padx=(0, 6), sticky="ew")

            ctk.CTkButton(
                style_row,
                text="EDIT",
                width=54,
                fg_color="#333333",
                hover_color="#444444",
                command=self.card_open_template_editor_for_styles
            ).grid(row=0, column=1, sticky="e")


    def card_save_values(self):
        template_name = self.card_selected_template.get()
        plain = self.card_values_plain()
        self.card_saved_values[template_name] = plain
        save_json(CARD_VALUES_PATH, self.card_saved_values)


    def card_values_plain(self):
        values = self.card_creator_values.get(self.card_selected_template.get(), {})
        return {k: (v.get() if hasattr(v, "get") else str(v)) for k, v in values.items()}





    def card_background_path(self):
        template_name = self.card_selected_template.get()
        if not template_name:
            return ""

        template = load_template(template_name)

        bg = background_path(template_name, template)
        if bg.exists():
            return str(bg)

        folder = template_dir(template_name)
        for candidate in [
            folder / "background.png",
            folder / "background.jpg",
            folder / "background.jpeg",
            folder / "background.webp",
        ]:
            if candidate.exists():
                return str(candidate)

        for ext in ("*.png", "*.jpg", "*.jpeg", "*.webp"):
            matches = list(folder.glob(ext))
            if matches:
                return str(matches[0])

        return ""


    def card_render_to_file(self, final=False):
        # First render to a temporary PNG using the existing layout engine, then apply export profile.
        temp = EXPORT_DIR / "_vadafok_card_temp_profile_source.png"
        render_template_card(self.card_template(), self.card_values_plain(), temp, self.card_background_path(), size=None)

        out = self.card_output_path(final=final)
        profile = self.card_export_profile.get() if hasattr(self, "card_export_profile") else "Broadcast PNG"
        img = Image.open(temp).convert("RGBA")
        export_engine.save_with_profile(img, out, profile)

        try:
            temp.unlink()
        except Exception:
            pass

        return out


    def card_update_preview(self):
        if not hasattr(self, "card_preview_frame"):
            return
        for w in self.card_preview_frame.winfo_children():
            w.destroy()
        self.card_creator_preview_image = None
        try:
            bg_path = self.card_background_path()
            if not bg_path:
                raise FileNotFoundError(f"Kein Background gefunden für Template: {self.card_selected_template.get()}")
            preview_path = self.card_render_to_file(final=False)
            img = Image.open(preview_path).convert("RGBA")
            original_size = img.size
            img.thumbnail((760, 620))
            if hasattr(self, "card_preview_info"):
                self.card_preview_info.configure(text=f"{self.card_selected_template.get()} | {original_size[0]}×{original_size[1]} | {self.card_export_profile.get()}")

            if hasattr(self, "card_export_profile_info"):
                profile = export_engine.get_export_profile(self.card_export_profile.get())
                size_text = "Originalgröße" if not profile.get("size") else f"{profile.get('size')[0]}×{profile.get('size')[1]}"
                fmt = profile.get("format", "PNG")
                self.card_export_profile_info.configure(text=f"{fmt} | {size_text}")
            self.card_creator_preview_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            ctk.CTkLabel(self.card_preview_frame, image=self.card_creator_preview_image, text="").place(relx=0.5, rely=0.5, anchor="center")
        except Exception as e:
            ctk.CTkLabel(self.card_preview_frame, text=f"Preview Fehler:\\n{e}", text_color="#D86A6A", wraplength=420, justify="center").place(relx=0.5, rely=0.5, anchor="center")

    def card_render_final(self):
        try:
            self.card_save_values()
            out = self.card_render_to_file(final=True)
            self.card_creator_last_render = out
            self.card_render_status.configure(text=f"Gerendert:\\n{out}", text_color="#8FE6A0")
            messagebox.showinfo("Card Creator", f"Karte gerendert:\\n{out}")
            self.card_update_preview()
        except Exception as e:
            messagebox.showerror("Card Creator", str(e))



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
        text = str(text or "").strip()
        if not text:
            return
        self.live_card_pending_text = text

        for attr in ("message_box", "message", "live_message", "live_card_message"):
            widget = getattr(self, attr, None)
            if widget is not None:
                try:
                    widget.delete("1.0", "end")
                    widget.insert("1.0", text)
                    return
                except Exception:
                    pass

    def live_card_get_message_text(self):
        for attr in ("message_box", "message", "live_message", "live_card_message"):
            widget = getattr(self, attr, None)
            if widget is not None:
                try:
                    return widget.get("1.0", "end").strip()
                except Exception:
                    pass
        return str(getattr(self, "live_card_pending_text", "") or "").strip()

    def live_card_apply_pending_text(self):
        text = str(getattr(self, "live_card_pending_text", "") or "").strip()
        if not text:
            return
        self.live_card_set_message_text(text)

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
        try:
            label = getattr(self, "status_label", None)
            if label is not None:
                if connected:
                    label.configure(text="● Connected", text_color="#6EE08C")
                else:
                    label.configure(text="● Not connected", text_color="#D86A6A")
        except Exception:
            pass


    def obs_workflow_log(self, message):
        if not hasattr(self, "obs_workflow_state"):
            self.obs_workflow_state = obs_workflow.OBSWorkflowState()
        self.obs_workflow_state.add_log(str(message))

    def obs_workflow_mark_command(self, message):
        if not hasattr(self, "obs_workflow_state"):
            self.obs_workflow_state = obs_workflow.OBSWorkflowState()
        self.obs_workflow_state.command(str(message))

    def obs_workflow_is_connected(self):
        obs_obj = getattr(self, "obs", None)
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
        connected_after_probe = False

        try:
            self.connect_obs()

            try:
                connected_after_probe = self.obs_workflow_is_connected()
            except Exception:
                connected_after_probe = False

            if hasattr(self.obs_workflow_state, "set_connected"):
                self.obs_workflow_state.set_connected(connected_after_probe)
            else:
                self.obs_workflow_state.connected = connected_after_probe

            self.obs_workflow_set_sidebar_status(connected_after_probe)

            if connected_after_probe:
                self.obs_workflow_state.last_error = ""
                if hasattr(self.obs_workflow_state, "add_event"):
                    self.obs_workflow_state.add_event("OBS connected")
                self.obs_workflow_mark_command("OBS connected")
                self.obs_workflow_refresh(silent=True)
            else:
                self.obs_workflow_state.last_error = "OBS probe failed after connect"
                self.obs_workflow_log("CONNECT ERROR: OBS probe failed after connect")
                messagebox.showerror("OBS Workflow", "OBS Verbindung wurde aufgebaut, aber die Statusprüfung ist fehlgeschlagen.")

        except Exception as e:
            try:
                if hasattr(self.obs_workflow_state, "set_connected"):
                    self.obs_workflow_state.set_connected(False)
                else:
                    self.obs_workflow_state.connected = False
            except Exception:
                pass
            self.obs_workflow_set_sidebar_status(False)
            self.obs_workflow_state.last_error = str(e)
            self.obs_workflow_log(f"CONNECT ERROR: {e}")
            messagebox.showerror("OBS Workflow", str(e))

        self.show_obs_workflow_page()


    def obs_workflow_disconnect(self):
        try:
            obs_obj = getattr(self, "obs", None)
            if obs_obj is not None:
                try:
                    obs_obj.disconnect()
                except Exception:
                    pass

            # Replace controller instance to guarantee no stale websocket/client is reused.
            self.obs = OBSController()

            if hasattr(self.obs_workflow_state, "set_connected"):
                self.obs_workflow_state.set_connected(False)
            else:
                self.obs_workflow_state.connected = False

            self.obs_workflow_set_sidebar_status(False)
            self.obs_workflow_state.last_error = ""

            if hasattr(self.obs_workflow_state, "add_event"):
                self.obs_workflow_state.add_event("OBS disconnected")
            self.obs_workflow_mark_command("OBS disconnected")

        except Exception as e:
            try:
                self.obs = OBSController()
            except Exception:
                pass
            try:
                self.obs_workflow_state.set_connected(False)
            except Exception:
                self.obs_workflow_state.connected = False
            self.obs_workflow_set_sidebar_status(False)
            self.obs_workflow_state.last_error = str(e)
            self.obs_workflow_log(f"DISCONNECT ERROR: {e}")
            messagebox.showerror("OBS Workflow", str(e))

        self.show_obs_workflow_page()


    def obs_workflow_refresh(self, silent=False):
        if not hasattr(self, "obs_workflow_state"):
            self.obs_workflow_state = obs_workflow.OBSWorkflowState()

        connected_now = self.obs_workflow_is_connected()
        if not connected_now:
            self.obs_workflow_log("OBS probe failed / disconnected")
        self.obs_workflow_set_sidebar_status(connected_now)
        if hasattr(self.obs_workflow_state, "set_connected"):
            self.obs_workflow_state.set_connected(connected_now)
        else:
            self.obs_workflow_state.connected = connected_now

        scenes = []
        sources = []

        try:
            obs = getattr(self, "obs", None)
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
                        self.obs_workflow_state.current_scene = obs.get_current_scene_name()
                    else:
                        self.obs_workflow_state.current_scene = obs.current_scene("")
                except Exception:
                    self.obs_workflow_state.current_scene = ""

                # Source cache, best effort
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
        except Exception as e:
            if hasattr(self.obs_workflow_state, "set_connected"):
                self.obs_workflow_state.set_connected(False)
            else:
                self.obs_workflow_state.connected = False
            self.obs_workflow_state.last_error = str(e)
            self.obs_workflow_log(f"REFRESH ERROR: {e}")

        if not scenes:
            scene_value = ""
            try:
                scene_value = self.scene_name.get()
            except Exception:
                scene_value = ""
            scenes = [scene_value] if scene_value else ["No scene cache yet"]

        if not sources:
            possible = []
            for attr in ("caption_group", "caption_text", "caption_banner_source", "caption_render_source", "scene_card_source"):
                var = getattr(self, attr, None)
                if var is not None:
                    try:
                        val = var.get()
                        if val:
                            possible.append(val)
                    except Exception:
                        pass
            sources = possible or ["No source cache yet"]

        self.obs_workflow_state.scenes = scenes
        self.obs_workflow_state.sources = sources
        if scenes and scenes != ["No scene cache yet"]:
            self.obs_workflow_log(f"Scene Cache updated: {len(scenes)} scene(s) loaded")
        self.obs_workflow_mark_command("OBS cache refreshed")
        if hasattr(self.obs_workflow_state, "add_event"):
            self.obs_workflow_state.add_event("OBS cache refreshed")

        if not silent:
            self.show_obs_workflow_page()


    def obs_workflow_banner_action(self, action, text=""):
        if not hasattr(self, "obs_workflow_state"):
            self.obs_workflow_state = obs_workflow.OBSWorkflowState()
        self.obs_workflow_state.set_connected(self.obs_workflow_is_connected()) if hasattr(self.obs_workflow_state, 'set_connected') else setattr(self.obs_workflow_state, 'connected', self.obs_workflow_is_connected())
        try:
            self.obs_workflow_state.banner(str(action), str(text or ""))
        except Exception:
            self.obs_workflow_mark_command(str(action))

    def obs_workflow_current_live_text(self):
        try:
            if hasattr(self, "live_card_get_message_text"):
                return self.live_card_get_message_text()
        except Exception:
            pass
        try:
            if hasattr(self, "message_box"):
                return self.message_box.get("1.0", "end").strip()
        except Exception:
            pass
        return ""



    def obs_workflow_load_scene_favorites(self):
        try:
            self.scene_favorites = scene_favorites.load_favorites()
        except Exception:
            self.scene_favorites = []
        return self.scene_favorites

    def obs_workflow_add_scene_favorite(self, scene_name):
        scene_name = str(scene_name or "").strip()
        if not scene_name or scene_name == "No scene cache yet":
            return
        self.scene_favorites = scene_favorites.add_favorite(scene_name)
        self.obs_workflow_log(f"Scene favorite added: {scene_name}")
        self.show_obs_workflow_page()

    def obs_workflow_remove_scene_favorite(self, scene_name):
        scene_name = str(scene_name or "").strip()
        if not scene_name:
            return
        self.scene_favorites = scene_favorites.remove_favorite(scene_name)
        self.obs_workflow_log(f"Scene favorite removed: {scene_name}")
        self.show_obs_workflow_page()

    def obs_workflow_switch_scene(self, scene_name):
        scene_name = str(scene_name or "").strip()
        if not scene_name or scene_name == "No scene cache yet":
            return

        if not self.ensure_obs_ready():
            return

        try:
            self.obs.switch_scene(scene_name)
            self.obs_workflow_state.current_scene = scene_name
            if hasattr(self.obs_workflow_state, "add_event"):
                self.obs_workflow_state.add_event(f"Scene switched: {scene_name}")
            self.obs_workflow_mark_command(f"Scene switched: {scene_name}")
            self.obs_workflow_refresh(silent=True)
            self.show_obs_workflow_page()
        except Exception as e:
            self.obs_workflow_state.last_error = str(e)
            self.obs_workflow_log(f"SCENE SWITCH ERROR: {e}")
            messagebox.showerror("Scene Switch", str(e))
            self.show_obs_workflow_page()

    def show_obs_workflow_page(self):
        self.set_active("OBS Workflow")
        self.clear_main()
        self.page_title("OBS Workflow")

        if not hasattr(self, "obs_workflow_state"):
            self.obs_workflow_state = obs_workflow.OBSWorkflowState()

        state = self.obs_workflow_state
        connected = self.obs_workflow_is_connected()
        if hasattr(state, "set_connected"):
            state.set_connected(connected)
        else:
            state.connected = connected

        outer = ctk.CTkFrame(self.main, fg_color=DARK)
        outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_columnconfigure(1, weight=1)
        outer.grid_rowconfigure(1, weight=0)
        outer.grid_rowconfigure(2, weight=1)

        status_box = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        status_box.grid(row=0, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 14))
        status_box.grid_columnconfigure(1, weight=1)

        status_text = "Connected" if connected else "Disconnected"
        status_color = "#8FE6A0" if connected else "#F08A8A"
        ctk.CTkLabel(status_box, text="OBS Status", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(16, 4), sticky="w")
        ctk.CTkLabel(status_box, text=status_text, text_color=status_color, font=ctk.CTkFont(size=18, weight="bold")).grid(row=1, column=0, padx=18, pady=(0, 14), sticky="w")

        info = []
        try:
            info.append(f"Host: {self.host.get()}")
            info.append(f"Port: {self.port.get()}")
            if self.scene_name.get():
                info.append(f"Scene optional: {self.scene_name.get()}")
        except Exception:
            pass
        ctk.CTkLabel(status_box, text="   ".join(info), text_color="#BCA870").grid(row=1, column=1, padx=18, pady=(0, 4), sticky="w")

        stats = []
        if getattr(state, "connected_since", ""):
            stats.append(f"Connected Since: {state.connected_since}")
        stats.append(f"Banner Commands: {getattr(state, 'banner_count', 0)}")
        if getattr(state, "current_scene", ""):
            stats.append(f"Current Scene: {state.current_scene}")
        if getattr(state, "last_banner_text", ""):
            stats.append(f"Last Banner Text: {state.last_banner_text[:60]}")
        ctk.CTkLabel(status_box, text="   ".join(stats), text_color="#888888").grid(row=2, column=1, padx=18, pady=(0, 14), sticky="w")

        btns = ctk.CTkFrame(status_box, fg_color="transparent")
        btns.grid(row=0, column=2, rowspan=3, padx=18, pady=14, sticky="e")
        ctk.CTkButton(btns, text="CONNECT", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=self.obs_workflow_connect).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="RECONNECT", fg_color="#333333", hover_color="#444444", command=self.obs_workflow_connect).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="DISCONNECT", fg_color="#5A1F1F", hover_color="#7A2A2A", command=self.obs_workflow_disconnect).pack(side="left", padx=4)
        ctk.CTkButton(btns, text="REFRESH", fg_color="#333333", hover_color="#444444", command=self.obs_workflow_refresh).pack(side="left", padx=4)

        favorites_box = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        favorites_box.grid(row=1, column=0, columnspan=2, sticky="ew", padx=0, pady=(0, 14))
        favorites_box.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(favorites_box, text="Scene Favorites", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(14, 6), sticky="w")

        self.obs_workflow_load_scene_favorites()
        fav_row = ctk.CTkFrame(favorites_box, fg_color="transparent")
        fav_row.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 14))

        if not self.scene_favorites:
            ctk.CTkLabel(fav_row, text="No favorite scenes yet. Use star in the Scenes list.", text_color="#777777").pack(side="left", padx=4)
        else:
            for fav_scene in self.scene_favorites:
                pill = ctk.CTkFrame(fav_row, fg_color="#0B0B0B", corner_radius=10)
                pill.pack(side="left", padx=4, pady=2)
                ctk.CTkButton(
                    pill,
                    text=fav_scene,
                    fg_color="#171717",
                    hover_color="#2C2C2C",
                    text_color="#D9C58C",
                    command=lambda s=fav_scene: self.obs_workflow_switch_scene(s)
                ).pack(side="left", padx=(6, 2), pady=6)
                ctk.CTkButton(
                    pill,
                    text="x",
                    width=34,
                    fg_color="#5A1F1F",
                    hover_color="#7A2A2A",
                    command=lambda s=fav_scene: self.obs_workflow_remove_scene_favorite(s)
                ).pack(side="left", padx=(2, 6), pady=6)

        scenes_box = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        scenes_box.grid(row=2, column=0, sticky="nsew", padx=(0, 7), pady=0)
        scenes_box.grid_columnconfigure(0, weight=1)
        scenes_box.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(scenes_box, text="Scenes", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")
        scenes_list = ctk.CTkScrollableFrame(scenes_box, fg_color="#0B0B0B", corner_radius=12)
        scenes_list.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        scenes_list.grid_columnconfigure(0, weight=1)
        current_scene = getattr(state, "current_scene", "")
        for idx, scene in enumerate(state.scenes or ["No scene cache yet"]):
            scene_text = str(scene)
            is_placeholder = scene_text == "No scene cache yet"
            is_current = scene_text == current_scene and not is_placeholder
            label_text = f"▶ {scene_text}" if is_current else scene_text
            label_color = GOLD if is_current else TEXT
            row_frame = ctk.CTkFrame(scenes_list, fg_color="#171717" if is_current else "transparent", corner_radius=8)
            row_frame.grid(row=idx, column=0, padx=6, pady=3, sticky="ew")
            row_frame.grid_columnconfigure(0, weight=1)

            scene_label = ctk.CTkLabel(row_frame, text=label_text, text_color=label_color, anchor="w")
            scene_label.grid(row=0, column=0, padx=10, pady=6, sticky="ew")
            if not is_placeholder:
                scene_label.bind("<Double-Button-1>", lambda _e, s=scene_text: self.obs_workflow_switch_scene(s))
                row_frame.bind("<Double-Button-1>", lambda _e, s=scene_text: self.obs_workflow_switch_scene(s))

            if not is_placeholder:
                is_fav = scene_text in getattr(self, "scene_favorites", [])
                ctk.CTkButton(
                    row_frame,
                    text="STAR" if is_fav else "ADD",
                    width=58,
                    fg_color=GOLD if is_fav else "#333333",
                    text_color="#111111" if is_fav else "#D9C58C",
                    hover_color=GOLD_DARK,
                    command=lambda s=scene_text, f=is_fav: self.obs_workflow_remove_scene_favorite(s) if f else self.obs_workflow_add_scene_favorite(s)
                ).grid(row=0, column=1, padx=(4, 4), pady=6)

                ctk.CTkButton(
                    row_frame,
                    text="SWITCH",
                    width=80,
                    fg_color=GOLD if not is_current else "#333333",
                    text_color="#111111" if not is_current else "#AAAAAA",
                    hover_color=GOLD_DARK,
                    command=lambda s=scene_text: self.obs_workflow_switch_scene(s)
                ).grid(row=0, column=2, padx=(4, 8), pady=6)

        sources_box = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        sources_box.grid(row=2, column=1, sticky="nsew", padx=(7, 0), pady=0)
        sources_box.grid_columnconfigure(0, weight=1)
        sources_box.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(sources_box, text="Sources", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")
        sources_list = ctk.CTkScrollableFrame(sources_box, fg_color="#0B0B0B", corner_radius=12)
        sources_list.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        sources_list.grid_columnconfigure(0, weight=1)
        for idx, source in enumerate(state.sources or ["No source cache yet"]):
            ctk.CTkLabel(sources_list, text=str(source), text_color=TEXT, anchor="w").grid(row=idx, column=0, padx=10, pady=5, sticky="ew")

        bottom = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        bottom.grid(row=3, column=0, columnspan=2, sticky="ew", padx=0, pady=(14, 0))
        bottom.grid_columnconfigure((0, 1, 2), weight=1)

        last = state.last_command or "No command yet"
        if state.last_command_time:
            last = f"{last}  ({state.last_command_time})"
        ctk.CTkLabel(bottom, text=f"Last Command: {last}", text_color="#BCA870", anchor="w").grid(row=0, column=0, columnspan=3, padx=18, pady=(14, 6), sticky="ew")

        if state.last_error:
            ctk.CTkLabel(bottom, text=f"Last Error: {state.last_error}", text_color="#F08A8A", anchor="w").grid(row=1, column=0, columnspan=3, padx=18, pady=(0, 6), sticky="ew")
            base_row = 2
        else:
            base_row = 1

        history_text = "\n".join(getattr(state, "banner_history", [])[-6:]) if getattr(state, "banner_history", []) else "No banner history yet."
        event_text = "\n".join(getattr(state, "obs_events", [])[-6:]) if getattr(state, "obs_events", []) else "No OBS events yet."
        log_text = "\n".join(state.log[-6:]) if state.log else "No workflow log yet."

        ctk.CTkLabel(bottom, text="Banner History", text_color=GOLD, anchor="w", font=ctk.CTkFont(size=14, weight="bold")).grid(row=base_row, column=0, padx=18, pady=(4, 2), sticky="ew")
        ctk.CTkLabel(bottom, text=history_text, text_color="#BCA870", justify="left", anchor="w").grid(row=base_row + 1, column=0, padx=18, pady=(0, 14), sticky="ew")

        ctk.CTkLabel(bottom, text="OBS Events", text_color=GOLD, anchor="w", font=ctk.CTkFont(size=14, weight="bold")).grid(row=base_row, column=1, padx=18, pady=(4, 2), sticky="ew")
        ctk.CTkLabel(bottom, text=event_text, text_color="#AAAAAA", justify="left", anchor="w").grid(row=base_row + 1, column=1, padx=18, pady=(0, 14), sticky="ew")

        ctk.CTkLabel(bottom, text="Workflow Log", text_color=GOLD, anchor="w", font=ctk.CTkFont(size=14, weight="bold")).grid(row=base_row, column=2, padx=18, pady=(4, 2), sticky="ew")
        ctk.CTkLabel(bottom, text=log_text, text_color="#888888", justify="left", anchor="w").grid(row=base_row + 1, column=2, padx=18, pady=(0, 14), sticky="ew")


    def show_settings_page(self):
        self.set_active("Settings")
        self.clear_main()
        self.page_title("Settings")
        box = ctk.CTkFrame(self.main, fg_color=PANEL, corner_radius=18)
        box.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        ctk.CTkLabel(box, text="VADAFOK Projektordner", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=24, pady=(24, 8))
        row = ctk.CTkFrame(box, fg_color="transparent")
        row.pack(fill="x", padx=24, pady=8)
        ctk.CTkEntry(row, textvariable=self.project_folder).pack(side="left", fill="x", expand=True)
        ctk.CTkButton(row, text="Durchsuchen...", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=self.browse_project_folder).pack(side="left", padx=8)
        ctk.CTkButton(box, text="SAVE SETTINGS", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=self.save_config).pack(anchor="w", padx=24, pady=18)

    def browse_project_folder(self):
        folder = filedialog.askdirectory(title="VADAFOK Projektordner wählen")
        if folder:
            self.project_folder.set(folder)
            self.save_config()

    def update_preview(self):
        if hasattr(self, "message_box"):
            self.update_render_preview()

    def open_quick_caption(self):
        if self.quick_window and self.quick_window.winfo_exists():
            self.quick_window.focus()
            return
        self.quick_window = ctk.CTkToplevel(self)
        self.quick_window.title("Quick Caption")
        self.quick_window.geometry("520x190")
        self.quick_window.attributes("-topmost", True)
        ctk.CTkLabel(self.quick_window, text="Quick Caption", font=ctk.CTkFont(size=20, weight="bold"), text_color=GOLD).pack(anchor="w", padx=16, pady=(14, 4))
        entry = ctk.CTkTextbox(self.quick_window, height=70, font=ctk.CTkFont(size=18), fg_color="#050505", border_color=GOLD_DARK, border_width=1)
        entry.pack(fill="both", expand=True, padx=16, pady=8)
        entry.focus_set()
        def send(_event=None):
            text = entry.get("1.0", "end").strip()
            if text:
                self.quick_window.destroy()
                self.quick_window = None
                self.show_live_card()
                self.set_message(text)
                self.show_card()
            return "break"
        entry.bind("<Return>", send)
        ctk.CTkButton(self.quick_window, text="SHOW", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=send).pack(fill="x", padx=16, pady=(0, 14))


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
        self.config_data.update({
            "host": self.host.get(),
            "port": self.port.get(),
            "password": self.password.get(),
            "scene_name": self.scene_name.get(),
            "caption_group": self.caption_group.get(),
            "caption_text": self.caption_text.get(),
            "caption_banner_source": self.caption_banner_source.get(),
            "caption_render_source": self.caption_render_source.get(),
            "scene_card_source": self.scene_card_source.get(),
            "duration": self.duration.get(),
            "style": self.style.get(),
            "project_folder": self.project_folder.get(),
            "caption_engine": self.caption_engine.get(),
            "caption_font_family": self.caption_font_family.get(),
            "caption_font_size": int(self.caption_font_size.get()),
            "caption_text_color": self.caption_text_color.get(),
            "caption_stroke_color": self.caption_stroke_color.get(),
            "caption_stroke_width": int(self.caption_stroke_width.get()),
            "caption_render_width": int(self.caption_render_width.get()),
            "caption_render_height": int(self.caption_render_height.get()),
            "caption_uppercase": bool(self.caption_uppercase.get()),
            "caption_safe_left": int(self.caption_safe_left.get()),
            "caption_safe_right": int(self.caption_safe_right.get()),
            "caption_safe_top": int(self.caption_safe_top.get()),
            "caption_safe_bottom": int(self.caption_safe_bottom.get()),
        })
        save_config(self.config_data)

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


    def render_smart_caption(self, text):
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
                self.render_status_label.configure(
                    text=f"🟢 Preview ready\nEngine: {self.caption_engine.get()}\nBanner: {'selected' if self.config_data.get('selected_banner_path') else 'none'}",
                    text_color="#8FE6A0"
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


    def show_card(self):
        if not self.ensure_obs_ready():
            return
        text = self.message_box.get("1.0", "end").strip() if hasattr(self, "message_box") else ""
        if not text: text = "..."
        try:
            scene = self.current_scene()

            selected_banner_path = self.config_data.get("selected_banner_path", "")

            if self.caption_engine.get() == "smart_png":
                try:
                    png = self.render_smart_caption(text)
                    self.obs.set_image_file(self.caption_render_source.get().strip(), png)
                except Exception:
                    messagebox.showerror("Caption Render Source nicht gefunden", f"Die OBS-Bildquelle '{self.caption_render_source.get().strip()}' wurde nicht gefunden.\n\nBitte OBS Connection prüfen.")
                    return

                try: self.obs.enable_source(scene, self.caption_text.get().strip(), False)
                except Exception: pass
                try: self.obs.enable_source(scene, self.caption_render_source.get().strip(), True)
                except Exception: pass
            else:
                if selected_banner_path:
                    try:
                        self.obs.set_image_file(self.caption_banner_source.get().strip(), selected_banner_path)
                    except Exception:
                        messagebox.showerror("Caption Banner Source nicht gefunden", f"Die OBS-Bildquelle '{self.caption_banner_source.get().strip()}' wurde nicht gefunden.\n\nBitte OBS Connection prüfen.")
                        return
                try:
                    self.obs.set_text(self.caption_text.get().strip(), text)
                except Exception:
                    messagebox.showerror("Text Source nicht gefunden", f"Die OBS-Textquelle '{self.caption_text.get().strip()}' wurde nicht gefunden.\n\nBitte OBS Connection prüfen.")
                    return

                try: self.obs.enable_source(scene, self.caption_render_source.get().strip(), False)
                except Exception: pass
                try: self.obs.enable_source(scene, self.caption_text.get().strip(), True)
                except Exception: pass

            self.obs.enable_source(scene, self.caption_group.get().strip(), True)

            if self.hide_timer:
                self.hide_timer.cancel()
            seconds = max(1, int(self.duration.get()))
            self.hide_timer = threading.Timer(seconds, lambda: self.after(0, self.hide_card))
            self.hide_timer.daemon = True
            self.hide_timer.start()
            self.save_config()
        except Exception as e:
            messagebox.showerror("SHOW fehlgeschlagen", str(e))
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
