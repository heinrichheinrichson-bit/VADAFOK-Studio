
import threading
from pathlib import Path
import customtkinter as ctk
from tkinter import messagebox, filedialog
from PIL import Image

from .core.config import load_config, save_config, load_favorites, save_favorites
from .core.library import scan_library, ROOT_FOLDERS
from .core.obs_controller import OBSController

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

        self.wm_title("VADAFOK Studio 0.2")
        self.geometry("1280x780")
        self.minsize(1100, 700)

        self.config_data = load_config()
        self.favorites = load_favorites()
        self.obs = OBSController()
        self.hide_timer = None
        self.quick_window = None
        self.thumbnail_refs = []
        self.library_items = []

        self.host = ctk.StringVar(value=self.config_data["host"])
        self.port = ctk.StringVar(value=self.config_data["port"])
        self.password = ctk.StringVar(value=self.config_data["password"])
        self.scene_name = ctk.StringVar(value=self.config_data["scene_name"])
        self.caption_group = ctk.StringVar(value=self.config_data["caption_group"])
        self.caption_text = ctk.StringVar(value=self.config_data["caption_text"])
        self.duration = ctk.StringVar(value=self.config_data["duration"])
        self.style = ctk.StringVar(value=self.config_data["style"])
        self.project_folder = ctk.StringVar(value=self.config_data.get("project_folder", ""))
        self.library_section = ctk.StringVar(value="All")
        self.search_text = ctk.StringVar(value="")

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
        ctk.CTkLabel(self.sidebar, text="Studio 0.2", text_color="#BCA870").pack(anchor="w", padx=20, pady=(0, 22))

        self.nav_buttons = {}
        pages = [
            ("Library", self.show_library),
            ("Live Card", self.show_live_card),
            ("Quick Cards", self.show_quick_cards),
            ("OBS Connection", self.show_obs_page),
            ("Settings", self.show_settings_page),
        ]
        for name, cmd in pages:
            btn = ctk.CTkButton(self.sidebar, text=name, height=42, corner_radius=10, anchor="w",
                                fg_color="transparent", hover_color=GOLD_DARK, text_color=TEXT, command=cmd)
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

        outer = ctk.CTkFrame(self.main, fg_color=PANEL, corner_radius=18)
        outer.grid(row=1, column=0, sticky="nsew", padx=24, pady=(0, 24))
        outer.grid_columnconfigure(0, weight=1)
        outer.grid_rowconfigure(2, weight=1)

        top = ctk.CTkFrame(outer, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 8))
        top.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(top, text="Section", text_color="#BCA870").grid(row=0, column=0, padx=(0, 8))
        sections = ["All"] + ROOT_FOLDERS
        ctk.CTkOptionMenu(top, values=sections, variable=self.library_section, fg_color="#1A1A1A", button_color=GOLD_DARK, command=lambda _: self.render_library_grid()).grid(row=0, column=1, sticky="w")

        ctk.CTkLabel(top, text="Search", text_color="#BCA870").grid(row=0, column=2, padx=(18, 8))
        entry = ctk.CTkEntry(top, textvariable=self.search_text, placeholder_text="Dateiname oder Kategorie...")
        entry.grid(row=0, column=3, sticky="ew")
        top.grid_columnconfigure(3, weight=1)
        entry.bind("<KeyRelease>", lambda e: self.render_library_grid())

        ctk.CTkButton(top, text="REFRESH", fg_color=GOLD, text_color="#111111", hover_color=GOLD_DARK, command=self.reload_library).grid(row=0, column=4, padx=(12, 0))

        self.library_info = ctk.CTkLabel(outer, text="", text_color="#D9C58C", anchor="w", justify="left")
        self.library_info.grid(row=1, column=0, sticky="ew", padx=18, pady=(0, 8))

        self.library_grid = ctk.CTkScrollableFrame(outer, fg_color="#0B0B0B", corner_radius=12)
        self.library_grid.grid(row=2, column=0, sticky="nsew", padx=18, pady=(0, 18))

        self.reload_library()

    def reload_library(self):
        self.library_items = scan_library(self.project_folder.get())
        self.render_library_grid()

    def render_library_grid(self):
        if not hasattr(self, "library_grid"):
            return
        for w in self.library_grid.winfo_children():
            w.destroy()
        self.thumbnail_refs = []

        section = self.library_section.get()
        query = self.search_text.get().strip().lower()
        items = self.library_items
        if section != "All":
            items = [i for i in items if i.section == section]
        if query:
            items = [i for i in items if query in i.name.lower() or query in i.category.lower() or query in i.relative.lower()]

        self.library_info.configure(text=f"Projektordner: {self.project_folder.get() or '(nicht gesetzt)'}    Gefundene Bilder: {len(items)}")

        if not items:
            ctk.CTkLabel(self.library_grid, text="Keine Bilder gefunden. Prüfe Settings > Projektordner.", text_color="#BCA870").grid(row=0, column=0, padx=18, pady=18, sticky="w")
            return

        cols = 4
        for idx, item in enumerate(items):
            r, c = divmod(idx, cols)
            card = ctk.CTkFrame(self.library_grid, fg_color="#151515", corner_radius=10)
            card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

            img_label = self.make_thumb_label(card, item.path)
            img_label.pack(padx=10, pady=(10, 6))
            img_label.bind("<Double-Button-1>", lambda e, it=item: self.library_item_double_click(it))

            ctk.CTkLabel(card, text=item.name, text_color=TEXT, wraplength=210, justify="center").pack(padx=10, pady=(0, 2))
            ctk.CTkLabel(card, text=f"{item.section} / {item.category}", text_color="#BCA870", wraplength=210, justify="center", font=ctk.CTkFont(size=12)).pack(padx=10, pady=(0, 10))

    def make_thumb_label(self, parent, path):
        try:
            img = Image.open(path).convert("RGBA")
            img.thumbnail((220, 124))
            thumb = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)
            self.thumbnail_refs.append(thumb)
            return ctk.CTkLabel(parent, image=thumb, text="")
        except Exception:
            return ctk.CTkLabel(parent, text="[Bild kann nicht geladen werden]", text_color="#D86A6A", width=220, height=124)

    def library_item_double_click(self, item):
        messagebox.showinfo("Library", f"Ausgewählt:\n{item.name}\n\nIn einer der nächsten Versionen kann Doppelklick direkt eine OBS-Quelle umschalten oder eine Scene Card anzeigen.")

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
        self.message_box.bind("<KeyRelease>", lambda e: self.update_preview())

        row = ctk.CTkFrame(left, fg_color="transparent")
        row.grid(row=2, column=0, sticky="ew", padx=18, pady=8)
        row.grid_columnconfigure((0, 1), weight=1)
        self.option(row, "Style", list(self.config_data["banner_sources"].keys()), self.style, 0)
        self.option(row, "Duration", ["3", "5", "7", "10", "15"], self.duration, 1)

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
        self.preview_frame.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="nsew")
        self.preview_label = ctk.CTkLabel(self.preview_frame, text="CHAT WAS RIGHT.", font=ctk.CTkFont(size=28, weight="bold"), text_color="#111111", fg_color=GOLD, corner_radius=18, width=360, height=82)
        self.preview_label.place(relx=0.5, rely=0.72, anchor="center")
        self.update_preview()

    def option(self, parent, label, values, var, col):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, padx=6, sticky="ew")
        ctk.CTkLabel(frame, text=label, text_color="#BCA870").pack(anchor="w")
        ctk.CTkOptionMenu(frame, values=values, variable=var, fg_color="#1A1A1A", button_color=GOLD_DARK, command=lambda _: self.update_preview()).pack(fill="x", pady=(6, 0))

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
        for label, var, hidden in [
            ("Host", self.host, False), ("Port", self.port, False), ("Password", self.password, True),
            ("Scene optional", self.scene_name, False), ("Caption Group", self.caption_group, False), ("Text Source", self.caption_text, False)
        ]:
            row = ctk.CTkFrame(box, fg_color="transparent")
            row.pack(fill="x", padx=24, pady=8)
            ctk.CTkLabel(row, text=label, width=150, anchor="w", text_color="#BCA870").pack(side="left")
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
        ctk.CTkLabel(box, text="Empfohlen: F:\\Bilder\\Vadafok\\Stream. Studio sucht dann in Library, Live Cards, Scene Cards, Banners, Templates, Fonts, Sounds und Projects.", wraplength=760, justify="left", text_color="#D9C58C").pack(anchor="w", padx=24, pady=8)

    def browse_project_folder(self):
        folder = filedialog.askdirectory(title="VADAFOK Projektordner wählen")
        if folder:
            self.project_folder.set(folder)
            self.save_config()

    def update_preview(self):
        if not hasattr(self, "preview_label") or not hasattr(self, "message_box"):
            return
        text = self.message_box.get("1.0", "end").strip() or "..."
        self.preview_label.configure(text=text.upper())
        style = self.style.get()
        if style == "Gold Ribbon":
            self.preview_label.configure(fg_color=GOLD, text_color="#111111")
        elif style == "Black Gold Plate":
            self.preview_label.configure(fg_color="#050505", text_color=GOLD)
        elif style == "Paper Scroll":
            self.preview_label.configure(fg_color="#E8C67A", text_color="#1B1000")
        elif style == "Film Strip":
            self.preview_label.configure(fg_color="#000000", text_color="#F7D66B")
        else:
            self.preview_label.configure(fg_color="#EAD9AA", text_color="#111111")

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
        self.config_data["host"] = self.host.get()
        self.config_data["port"] = self.port.get()
        self.config_data["password"] = self.password.get()
        self.config_data["scene_name"] = self.scene_name.get()
        self.config_data["caption_group"] = self.caption_group.get()
        self.config_data["caption_text"] = self.caption_text.get()
        self.config_data["duration"] = self.duration.get()
        self.config_data["style"] = self.style.get()
        self.config_data["project_folder"] = self.project_folder.get()
        save_config(self.config_data)

    def current_scene(self):
        return self.obs.current_scene(self.scene_name.get().strip())

    def show_card(self):
        if not self.obs.connected:
            messagebox.showwarning("Nicht verbunden", "Bitte zuerst OBS verbinden.")
            return
        text = self.message_box.get("1.0", "end").strip() if hasattr(self, "message_box") else ""
        if not text:
            text = "..."
        try:
            scene = self.current_scene()
            self.obs.set_text(self.caption_text.get().strip(), text)
            selected = self.config_data["banner_sources"].get(self.style.get())
            for banner in self.config_data["banner_sources"].values():
                try:
                    self.obs.enable_source(scene, banner, banner == selected)
                except Exception:
                    pass
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
        if not self.obs.connected:
            return
        try:
            self.obs.enable_source(self.current_scene(), self.caption_group.get().strip(), False)
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

    def save_current_quick(self):
        if not hasattr(self, "message_box"):
            return
        text = self.message_box.get("1.0", "end").strip()
        if not text:
            return
        self.favorites.setdefault("Custom", [])
        if text not in self.favorites["Custom"]:
            self.favorites["Custom"].append(text)
            save_favorites(self.favorites)
        messagebox.showinfo("Quick Card", "Gespeichert.")

    def set_message(self, text):
        if not hasattr(self, "message_box"):
            return
        self.message_box.delete("1.0", "end")
        self.message_box.insert("1.0", text)
        self.update_preview()

    def use_favorite(self, text):
        self.show_live_card()
        self.set_message(text)

def main():
    app = VadafokStudio()
    app.mainloop()
