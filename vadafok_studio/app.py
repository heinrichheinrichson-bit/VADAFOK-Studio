
import os
import tkinter as tk
from tkinter import filedialog
import threading
import customtkinter as ctk
from tkinter import messagebox, filedialog, simpledialog
from PIL import Image

from .core.config import TEMPLATE_PROFILES_PATH, load_config, save_config, load_favorites, save_favorites, load_asset_meta, save_asset_meta, EXPORT_DIR, load_json, save_json, CARD_VALUES_PATH
from .core.library import scan_library, ROOT_FOLDERS, guessed_tags
from .core.obs_controller import OBSController
from .core.caption_renderer import render_caption_png
from .core.template_store import list_templates, load_template, save_template, create_template, set_background_from_file, background_path, import_legacy_templates, delete_template, duplicate_template, rename_template, set_default_template, get_default_template, ensure_background_file, template_dir
from .core.image_view import load_rgba, fit_image_to_box, pil_to_tk_photo_data, image_status
from .core.layout_engine import banner_profile_to_layout_field, apply_layout_field_to_banner_profile, create_default_template, render_template_card
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
        self.wm_title("VADAFOK Studio 2.5.5.1")
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
        self.template_drag_mode = None
        self.template_drag_start = None
        self.template_drag_original = None
        self.template_working_data = None
        self.template_zoom_factor = 1.0
        self.template_zoom_label_var = ctk.StringVar(value="100%")
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
        self.obs = OBSController()
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
        ctk.CTkLabel(self.sidebar, text="Studio 2.5.5", text_color="#BCA870").pack(anchor="w", padx=20, pady=(0, 22))
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
        outer.grid_columnconfigure(1, weight=3)
        outer.grid_columnconfigure(2, weight=1)
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
        self.message_box.insert("1.0", "CHAT WAS RIGHT.")
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
        ctk.CTkLabel(box, text="Studio 2.5.5: smart_png rendert Banner + Text als fertige PNG. OBS braucht dafür nur die Bildquelle 'VADAFOK Caption Render'.", text_color="#D9C58C", wraplength=780, justify="left").pack(anchor="w", padx=24, pady=12)
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
        outer.grid_columnconfigure(1, weight=3)
        outer.grid_columnconfigure(2, weight=1)
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


        props = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        props.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
        props.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            props,
            text="Properties",
            text_color=GOLD,
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

        self.template_props_body = ctk.CTkFrame(props, fg_color="#0B0B0B", corner_radius=12)
        self.template_props_body.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        self.template_props_body.grid_columnconfigure(1, weight=1)

        self.template_build_properties_panel()


        zoom_bar = ctk.CTkFrame(controls, fg_color="transparent")
        zoom_bar.grid(row=2, column=0, columnspan=5, padx=4, pady=(8, 0), sticky="ew")
        zoom_bar.grid_columnconfigure(1, weight=1)
        ctk.CTkButton(zoom_bar, text="ZOOM -", fg_color="#333333", hover_color="#444444", command=self.template_zoom_out).grid(row=0, column=0, padx=(0, 4), sticky="ew")
        ctk.CTkLabel(zoom_bar, textvariable=self.template_zoom_label_var, text_color=GOLD, font=ctk.CTkFont(size=14, weight="bold")).grid(row=0, column=1, padx=4, sticky="ew")
        ctk.CTkButton(zoom_bar, text="ZOOM +", fg_color="#333333", hover_color="#444444", command=self.template_zoom_in).grid(row=0, column=2, padx=4, sticky="ew")
        ctk.CTkButton(zoom_bar, text="100%", fg_color="#333333", hover_color="#444444", command=self.template_zoom_reset).grid(row=0, column=3, padx=(4, 0), sticky="ew")

        self.template_draw_canvas()

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
        self.show_template_editor_page()


    def template_select(self, name):
        self.template_selected_name = name
        self.template_selected_field = None
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
        template = self.template_current()
        if self.template_selected_field is None:
            messagebox.showwarning("Template Editor", "Bitte zuerst ein Feld auswählen.")
            return
        if not (0 <= self.template_selected_field < len(template.get("fields", []))):
            messagebox.showwarning("Template Editor", "Ausgewähltes Feld wurde nicht gefunden.")
            return

        source = dict(template["fields"][self.template_selected_field])
        base_name = source.get("name", "field")
        existing = {f.get("name", "") for f in template.get("fields", [])}

        candidate = f"{base_name}_copy"
        index = 2
        while candidate in existing:
            candidate = f"{base_name}_copy{index}"
            index += 1

        copied = dict(source)
        copied["name"] = candidate

        design_w, design_h = getattr(self, "template_canvas_design_size", (1280, 720))
        copied["x"] = min(max(0, int(copied.get("x", 0)) + 15), max(0, int(design_w) - int(copied.get("width", 100))))
        copied["y"] = min(max(0, int(copied.get("y", 0)) + 15), max(0, int(design_h) - int(copied.get("height", 50))))

        template.setdefault("fields", []).append(copied)
        self.template_selected_field = len(template["fields"]) - 1

        save_template(self.template_selected_name, template)
        self.template_load_selected_properties()
        self.template_draw_canvas()

        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()

        try:
            if hasattr(self, "template_prop_name_entry"):
                self.template_prop_name_entry.focus_set()
                self.template_prop_name_entry.select_range(0, "end")
        except Exception:
            pass


    def template_delete_field(self):
        template = self.template_current()
        if self.template_selected_field is None:
            return
        if 0 <= self.template_selected_field < len(template["fields"]):
            del template["fields"][self.template_selected_field]
            self.template_selected_field = None
            self.template_load_selected_properties()
            save_template(self.template_selected_name, template)
            self.template_draw_canvas()




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
                offset = ((cw - display.size[0]) // 2, (ch - display.size[1]) // 2)
                self.template_canvas_scale = scale
                self.template_canvas_offset = offset
                self.template_bg_photo = tk.PhotoImage(data=pil_to_tk_photo_data(display))
                canvas.create_image(offset[0], offset[1], image=self.template_bg_photo, anchor="nw", tags="background")
                canvas.create_rectangle(offset[0], offset[1], offset[0] + display.size[0], offset[1] + display.size[1], outline="#3A2A0D", width=2)
            except Exception as e:
                self.template_canvas_scale = min((cw - 40) / 1280, (ch - 40) / 720) * float(getattr(self, 'template_zoom_factor', 1.0))
                self.template_canvas_offset = ((cw - int(1280 * self.template_canvas_scale)) // 2, (ch - int(720 * self.template_canvas_scale)) // 2)
                ox, oy = self.template_canvas_offset
                dw, dh = int(1280 * self.template_canvas_scale), int(720 * self.template_canvas_scale)
                canvas.create_rectangle(ox, oy, ox + dw, oy + dh, fill="#111111", outline="#3A2A0D", width=2)
                canvas.create_text(ox + 20, oy + 20, text=f"Background Fehler:\n{e}", anchor="nw", fill="#D86A6A", font=("Arial", 14, "bold"))
        else:
            self.template_canvas_scale = min((cw - 40) / 1280, (ch - 40) / 720) * float(getattr(self, 'template_zoom_factor', 1.0))
            self.template_canvas_offset = ((cw - int(1280 * self.template_canvas_scale)) // 2, (ch - int(720 * self.template_canvas_scale)) // 2)
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

    def template_update_fields_overlay(self, bg_info=None):
        if not hasattr(self, "template_canvas"):
            return
        canvas = self.template_canvas
        self.template_clear_fields_overlay()
        template = self.template_current()

        if bg_info is None:
            try:
                bg_path = str(background_path(self.template_selected_name, template))
                bg_info = image_status(bg_path)
            except Exception:
                bg_info = {"name": "?", "exists": False}

        for idx, field in enumerate(template.get("fields", [])):
            x1, y1, x2, y2 = self.template_field_screen_rect(field)
            selected = idx == self.template_selected_field
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
            if self.template_selected_field is not None and 0 <= self.template_selected_field < len(template.get("fields", [])):
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

    def template_mouse_down(self, event):
        idx, mode = self.template_hit_test(event.x, event.y)

        # Klick ins leere Canvas:
        # Wenn nichts ausgewählt war, gar nichts neu zeichnen.
        # Wenn ein Feld ausgewählt war, nur Overlay aktualisieren, um Handles zu entfernen.
        if idx is None:
            had_selection = self.template_selected_field is not None
            self.template_selected_field = None
            self.template_drag_mode = None
            self.template_drag_start = None
            self.template_drag_original = None
            self.template_load_selected_properties()
            if hasattr(self, "template_props_body"):
                self.template_build_properties_panel()
            if had_selection:
                self.template_update_fields_overlay()
            return

        self.template_selected_field = idx
        self.template_load_selected_properties()
        if hasattr(self, "template_props_body"):
            self.template_build_properties_panel()

        self.template_drag_mode = mode
        self.template_drag_start = (event.x, event.y)
        template = self.template_current()
        self.template_drag_original = dict(template["fields"][idx])

        # Nur Overlay neu zeichnen. Hintergrund bleibt stehen.
        self.template_update_fields_overlay()


    def template_mouse_drag(self, event):
        if self.template_selected_field is None or self.template_drag_original is None:
            return

        template = self.template_current()
        sx, sy = self.template_drag_start
        dx = int((event.x - sx) / self.template_canvas_scale)
        dy = int((event.y - sy) / self.template_canvas_scale)

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

        f["x"], f["y"], f["width"], f["height"] = int(x), int(y), int(w), int(h)
        template["fields"][self.template_selected_field] = f
        self.template_update_fields_overlay()


    def template_mouse_up(self, event):
        save_template(self.template_selected_name, self.template_current())
        self.template_drag_mode = None
        self.template_drag_start = None
        self.template_drag_original = None


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

        outer = ctk.CTkFrame(self.main, fg_color=DARK)
        outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_columnconfigure(1, weight=3)
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
            ctk.CTkButton(tlist, text=prefix + name, anchor="w", fg_color="#171717", hover_color="#2C2C2C", command=lambda n=name: self.card_select_template(n)).pack(fill="x", padx=8, pady=4)

        preview = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        preview.grid(row=0, column=1, sticky="nsew", padx=12)
        preview.grid_columnconfigure(0, weight=1)
        preview.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(preview, text="Preview", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")
        self.card_preview_frame = ctk.CTkFrame(preview, fg_color="#050505", corner_radius=14, border_color="#3A2A0D", border_width=1)
        self.card_preview_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))

        form = ctk.CTkFrame(outer, fg_color=PANEL, corner_radius=18)
        form.grid(row=0, column=2, sticky="nsew", padx=(12, 0))
        form.grid_columnconfigure(0, weight=1)
        form.grid_rowconfigure(1, weight=1)
        ctk.CTkLabel(form, text="Card Data", text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).grid(row=0, column=0, padx=18, pady=(18, 8), sticky="w")

        self.card_form_frame = ctk.CTkScrollableFrame(form, fg_color="#0B0B0B", corner_radius=12)
        self.card_form_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 12))
        self.card_form_frame.grid_columnconfigure(0, weight=1)

        buttons = ctk.CTkFrame(form, fg_color="transparent")
        buttons.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))
        buttons.grid_columnconfigure(0, weight=1)
        ctk.CTkButton(buttons, text="RENDER CARD", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=self.card_render_final).grid(row=0, column=0, padx=0, pady=4, sticky="ew")
        self.card_render_status = ctk.CTkLabel(buttons, text="Noch nicht gerendert.", text_color="#BCA870", wraplength=260, justify="left")
        self.card_render_status.grid(row=1, column=0, pady=(8, 0), sticky="w")

        self.card_build_form()
        self.card_update_preview()



    def card_select_template(self, name):
        self.card_selected_template.set(name)
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

        for row, field in enumerate(fields):
            name = field.get("name", f"field_{row+1}")
            saved = self.card_saved_values.get(self.card_selected_template.get(), {})
            if name not in values or not hasattr(values.get(name), "get"):
                values[name] = ctk.StringVar(value=str(saved.get(name, "")))
            label = name.replace("_", " ").title()
            ctk.CTkLabel(self.card_form_frame, text=label, text_color="#BCA870").grid(row=row*2, column=0, padx=12, pady=(10, 2), sticky="w")
            entry = ctk.CTkEntry(self.card_form_frame, textvariable=values[name])
            entry.grid(row=row*2+1, column=0, padx=12, pady=(0, 8), sticky="ew")
            entry.bind("<KeyRelease>", lambda e: (self.card_save_values(), self.card_update_preview()))


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
        suffix = "final" if final else "preview"
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in self.card_selected_template.get())
        out = EXPORT_DIR / f"card_{safe_name}_{suffix}.png"
        render_template_card(self.card_template(), self.card_values_plain(), out, self.card_background_path(), size=None)
        return out


    def card_update_preview(self):
        if not hasattr(self, "card_preview_frame"):
            return
        for w in self.card_preview_frame.winfo_children():
            w.destroy()
        self.card_creator_preview_image = None
        try:
            if not self.card_background_path():
                raise FileNotFoundError(f"Kein Background gefunden für Template: {self.card_selected_template.get()}")
            if not self.card_background_path():
                raise FileNotFoundError(f"Kein Background gefunden für Template: {self.card_selected_template.get()}")
            preview_path = self.card_render_to_file(final=False)
            img = Image.open(preview_path).convert("RGBA")
            img.thumbnail((620, 520))
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


    def show_quick_cards(self):
        self.set_active("Quick Cards")
        self.clear_main()
        self.page_title("Quick Cards")
        box = ctk.CTkScrollableFrame(self.main, fg_color=PANEL, corner_radius=18)
        box.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        for category, items in self.favorites.items():
            ctk.CTkLabel(box, text=category, text_color=GOLD, font=ctk.CTkFont(size=18, weight="bold")).pack(anchor="w", padx=18, pady=(18, 6))
            for fav in items:
                ctk.CTkButton(box, text=fav, height=42, fg_color="#171717", hover_color="#2C2C2C", anchor="w", command=lambda t=fav: self.use_favorite(t)).pack(fill="x", padx=18, pady=4)

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
        if self.obs.connected:
            return True
        try:
            self.obs.connect(self.host.get().strip(), self.port.get().strip(), self.password.get())
            self.status_label.configure(text="● Connected", text_color="#6EE08C")
            self.save_config()
            return True
        except Exception as e:
            messagebox.showerror("OBS Verbindung fehlgeschlagen", str(e))
            self.status_label.configure(text="● Not connected", text_color="#D86A6A")
            return False

    def connect_obs(self):
        try:
            self.obs.connect(self.host.get().strip(), self.port.get().strip(), self.password.get())
            self.status_label.configure(text="● Connected", text_color="#6EE08C")
            self.save_config()
            messagebox.showinfo("OBS", "Verbindung erfolgreich.")
        except Exception as e:
            self.status_label.configure(text="● Not connected", text_color="#D86A6A")
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

    def hide_card(self):
        if not self.obs.connected: return
        try: self.obs.enable_source(self.current_scene(), self.caption_group.get().strip(), False)
        except Exception: pass

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

    def save_current_quick(self):
        if not hasattr(self, "message_box"): return
        text = self.message_box.get("1.0", "end").strip()
        if not text: return
        self.favorites.setdefault("Custom", [])
        if text not in self.favorites["Custom"]:
            self.favorites["Custom"].append(text)
            save_favorites(self.favorites)
        messagebox.showinfo("Quick Card", "Gespeichert.")

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
