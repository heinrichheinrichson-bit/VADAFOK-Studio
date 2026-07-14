"""Banner favorites workflow for the Live Card page.

This extension deliberately reuses the Library's existing favorites metadata.
It does not create a second banner database and does not modify banner files.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import customtkinter as ctk
from PIL import Image

_INSTALLED = False
_MAX_FAVORITES = 4


def _same_path(left: Any, right: Any) -> bool:
    try:
        return Path(str(left)).resolve() == Path(str(right)).resolve()
    except Exception:
        return str(left or "") == str(right or "")


def _load_banner_favorites(app: Any) -> list[Any]:
    """Load up to four favorite image banners from the existing Library."""
    try:
        from vadafok_studio.app import scan_library_section

        items: Iterable[Any] = scan_library_section(
            app.project_folder.get(),
            "Banners",
        )
    except Exception as exc:
        print(f"[Banner Workflow] could not scan Banners: {exc}")
        return []

    result: list[Any] = []
    for item in items:
        try:
            if getattr(item, "kind", "") != "image":
                continue
            if not app.item_is_favorite(item):
                continue
            result.append(item)
            if len(result) >= _MAX_FAVORITES:
                break
        except Exception:
            continue
    return result


def _select_favorite_banner(app: Any, item: Any) -> None:
    """Select a favorite through the application's normal config path."""
    try:
        from vadafok_studio.app import save_config

        app.config_data["selected_banner_path"] = str(item.path)
        save_config(app.config_data)
        app.show_live_card()
    except Exception as exc:
        try:
            from tkinter import messagebox

            messagebox.showerror(
                "Banner Favorites",
                f"Banner konnte nicht ausgewählt werden.\n\n{exc}",
            )
        except Exception:
            print(f"[Banner Workflow] selection failed: {exc}")


def _make_thumbnail(app: Any, parent: Any, path: Any) -> Any:
    try:
        image = Image.open(path).convert("RGBA")
        image.thumbnail((180, 82))
        thumb = ctk.CTkImage(
            light_image=image,
            dark_image=image,
            size=image.size,
        )
        app.banner_favorite_thumb_refs.append(thumb)
        return ctk.CTkLabel(parent, image=thumb, text="")
    except Exception:
        return ctk.CTkLabel(
            parent,
            text="VORSCHAU\nNICHT VERFÜGBAR",
            width=180,
            height=82,
            text_color="#D86A6A",
            fg_color="#090909",
            corner_radius=8,
        )


def _render_banner_favorites(app: Any) -> None:
    """Add a compact four-slot favorites strip below the Live Card area."""
    try:
        if str(getattr(app, "active_page", "")) != "Live Card":
            return
        main = getattr(app, "main", None)
        if main is None or not main.winfo_exists():
            return

        old = getattr(app, "banner_favorites_frame", None)
        if old is not None and old.winfo_exists():
            old.destroy()

        from vadafok_studio.app import GOLD, GOLD_DARK, PANEL, TEXT

        frame = ctk.CTkFrame(
            main,
            fg_color=PANEL,
            corner_radius=14,
            border_color="#3A2A0D",
            border_width=1,
        )
        frame.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=28,
            pady=(0, 18),
        )
        frame.grid_columnconfigure(1, weight=1)
        app.banner_favorites_frame = frame
        app.banner_favorite_thumb_refs = []

        title_box = ctk.CTkFrame(frame, fg_color="transparent")
        title_box.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(10, 4))
        title_box.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            title_box,
            text="★ BANNER FAVORITES",
            text_color=GOLD,
            font=ctk.CTkFont(size=15, weight="bold"),
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(
            title_box,
            text="CHANGE / MANAGE",
            width=140,
            height=28,
            fg_color="#333333",
            hover_color="#444444",
            command=app.open_live_card_banner_picker,
        ).grid(row=0, column=1, sticky="e")

        content = ctk.CTkFrame(frame, fg_color="transparent")
        content.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(2, 12))
        for column in range(_MAX_FAVORITES):
            content.grid_columnconfigure(column, weight=1)

        favorites = _load_banner_favorites(app)
        current = app.config_data.get("selected_banner_path", "")

        if not favorites:
            empty = ctk.CTkFrame(
                content,
                fg_color="#101010",
                corner_radius=10,
                border_color="#2A2A2A",
                border_width=1,
            )
            empty.grid(row=0, column=0, columnspan=4, sticky="ew", padx=5, pady=4)
            empty.grid_columnconfigure(0, weight=1)
            ctk.CTkLabel(
                empty,
                text=(
                    "Noch keine Banner-Favoriten. Öffne die Banner Library und "
                    "markiere bis zu vier Banner mit TOGGLE FAVORITE ⭐."
                ),
                text_color="#BCA870",
                wraplength=760,
                justify="left",
            ).grid(row=0, column=0, padx=14, pady=12, sticky="w")
            ctk.CTkButton(
                empty,
                text="OPEN BANNER LIBRARY",
                width=170,
                fg_color=GOLD,
                text_color="#111111",
                hover_color=GOLD_DARK,
                command=app.open_live_card_banner_picker,
            ).grid(row=0, column=1, padx=14, pady=10)
            return

        for index, item in enumerate(favorites):
            active = _same_path(current, item.path)
            card = ctk.CTkFrame(
                content,
                fg_color="#151515",
                corner_radius=10,
                border_color=GOLD if active else "#292929",
                border_width=2 if active else 1,
            )
            card.grid(row=0, column=index, sticky="nsew", padx=5, pady=4)
            card.grid_columnconfigure(0, weight=1)

            image_label = _make_thumbnail(app, card, item.path)
            image_label.grid(row=0, column=0, padx=8, pady=(8, 4))

            name = str(getattr(item, "name", Path(str(item.path)).stem))
            ctk.CTkLabel(
                card,
                text=("ACTIVE · " if active else "") + name,
                text_color=GOLD if active else TEXT,
                font=ctk.CTkFont(size=11, weight="bold" if active else "normal"),
                wraplength=175,
            ).grid(row=1, column=0, padx=8, pady=(0, 7))

            for widget in (card, image_label):
                widget.bind(
                    "<Button-1>",
                    lambda _event, selected=item: _select_favorite_banner(app, selected),
                )

        for index in range(len(favorites), _MAX_FAVORITES):
            slot = ctk.CTkButton(
                content,
                text="＋\nADD FAVORITE",
                height=112,
                fg_color="#101010",
                hover_color="#242424",
                border_color="#2A2A2A",
                border_width=1,
                text_color="#8F8058",
                command=app.open_live_card_banner_picker,
            )
            slot.grid(row=0, column=index, sticky="nsew", padx=5, pady=4)
    except Exception as exc:
        print(f"[Banner Workflow] render failed: {exc}")


def install_banner_workflow() -> None:
    """Install the Live Card banner favorites extension once."""
    global _INSTALLED
    if _INSTALLED:
        return

    from vadafok_studio.app import VadafokStudio

    original_show_live_card = VadafokStudio.show_live_card

    def workflow_show_live_card(self: Any, *args: Any, **kwargs: Any) -> Any:
        result = original_show_live_card(self, *args, **kwargs)
        try:
            self.after(0, lambda: _render_banner_favorites(self))
        except Exception:
            pass
        return result

    VadafokStudio.show_live_card = workflow_show_live_card
    _INSTALLED = True
