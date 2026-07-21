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
    """Load the four most recently marked favorite image banners.

    Library favorites are stored in selection order. The previous code scanned
    the Banners folder and returned the first four matching files, so a newly
    marked favorite could remain invisible whenever older favorites were found
    first. Reading the metadata order backwards makes CHANGE / MANAGE behave
    like a real four-slot switcher: the newest choice is visible immediately.
    """
    try:
        from vadafok_studio.app import scan_library_section

        items: Iterable[Any] = scan_library_section(
            app.project_folder.get(),
            "Banners",
        )
    except Exception as exc:
        print(f"[Banner Workflow] could not scan Banners: {exc}")
        return []

    banner_items: dict[str, Any] = {}
    for item in items:
        try:
            if getattr(item, "kind", "") == "image":
                banner_items[str(app.item_key(item))] = item
        except Exception:
            continue

    favorite_keys = list(
        getattr(app, "asset_meta", {}).get("favorites", []) or []
    )
    result: list[Any] = []
    for key in reversed(favorite_keys):
        item = banner_items.get(str(key))
        if item is None:
            continue
        result.append(item)
        if len(result) >= _MAX_FAVORITES:
            break

    return result


def _load_banner_slots(app: Any) -> list[Any | None]:
    """Load four stable slots, migrating the former recent-favorites strip."""
    raw_slots = app.config_data.get("live_card_banner_slots")
    configured = bool(app.config_data.get("live_card_banner_slots_initialized"))
    if configured:
        paths = (
            (list(raw_slots) if isinstance(raw_slots, list) else [])
            + ["", "", "", ""]
        )[:_MAX_FAVORITES]
    else:
        favorites = _load_banner_favorites(app)
        paths = [str(item.path) for item in favorites]
        paths = (paths + ["", "", "", ""])[:_MAX_FAVORITES]
        try:
            from vadafok_studio.app import save_config
            app.config_data["live_card_banner_slots"] = paths
            app.config_data["live_card_banner_slots_initialized"] = True
            save_config(app.config_data)
        except Exception:
            pass

    slots: list[Any | None] = []
    for path_value in paths:
        path = Path(str(path_value)) if str(path_value).strip() else None
        if path is None or not path.exists():
            slots.append(None)
        else:
            slots.append(type("BannerSlot", (), {"path": path, "name": path.name})())
    return slots


def _clear_banner_slot(app: Any, index: int) -> None:
    try:
        from vadafok_studio.app import save_config
        slots = app.config_data.get("live_card_banner_slots", [])
        slots = (list(slots) + ["", "", "", ""])[:_MAX_FAVORITES]
        slots[index] = ""
        app.config_data["live_card_banner_slots"] = slots
        app.config_data["live_card_banner_slots_initialized"] = True
        save_config(app.config_data)
        _render_banner_favorites(app)
    except Exception as exc:
        print(f"[Banner Workflow] slot removal failed: {exc}")


def _select_favorite_banner(app: Any, item: Any) -> None:
    """Select a favorite without rebuilding the complete Live Card page."""
    try:
        from vadafok_studio.app import save_config

        app.config_data["selected_banner_path"] = str(item.path)
        save_config(app.config_data)

        # Update only the widgets affected by the banner selection. Reopening
        # the complete Live Card page caused a visible flash on every click.
        label = getattr(app, "live_card_banner_name_label", None)
        if label is not None and label.winfo_exists():
            label.configure(text=app.live_card_current_banner_name())

        app.update_render_preview()
        _refresh_banner_slot_selection(app)
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


def _refresh_banner_slot_selection(app: Any) -> None:
    """Refresh only active styling, never rebuild thumbnails or the page."""
    current = app.config_data.get("selected_banner_path", "")
    for card, label, item in getattr(app, "banner_favorite_cards", []):
        try:
            if not card.winfo_exists():
                continue
            active = _same_path(current, item.path)
            card.configure(
                border_color="#D6A43A" if active else "#292929",
                border_width=2 if active else 1,
            )
            name = str(getattr(item, "name", Path(str(item.path)).stem))
            label.configure(
                text=("ACTIVE · " if active else "") + name,
                text_color="#D6A43A" if active else "#F2E2B6",
                font=ctk.CTkFont(size=11, weight="bold" if active else "normal"),
            )
        except Exception:
            continue


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
        app.banner_favorite_cards = []

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
            text="BANNER LIBRARY",
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

        favorites = _load_banner_slots(app)
        current = app.config_data.get("selected_banner_path", "")

        for index, item in enumerate(favorites):
            if item is None:
                slot = ctk.CTkButton(
                    content,
                    text=f"＋\nSET FAVORITE {index + 1}",
                    height=138,
                    fg_color="#101010",
                    hover_color="#242424",
                    border_color="#2A2A2A",
                    border_width=1,
                    text_color="#8F8058",
                    command=lambda target=index: app.open_live_card_banner_picker(target),
                )
                slot.grid(row=0, column=index, sticky="nsew", padx=5, pady=4)
                continue
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
            name_label = ctk.CTkLabel(
                card,
                text=("ACTIVE · " if active else "") + name,
                text_color=GOLD if active else TEXT,
                font=ctk.CTkFont(size=11, weight="bold" if active else "normal"),
                wraplength=175,
            )
            name_label.grid(row=1, column=0, padx=8, pady=(0, 7))
            app.banner_favorite_cards.append((card, name_label, item))

            slot_actions = ctk.CTkFrame(card, fg_color="transparent")
            slot_actions.grid(row=2, column=0, padx=7, pady=(0, 7), sticky="ew")
            slot_actions.grid_columnconfigure((0, 1), weight=1)
            ctk.CTkButton(
                slot_actions,
                text="REPLACE",
                height=25,
                fg_color="#333333",
                hover_color="#444444",
                command=lambda target=index: app.open_live_card_banner_picker(target),
            ).grid(row=0, column=0, padx=(0, 3), sticky="ew")
            ctk.CTkButton(
                slot_actions,
                text="REMOVE",
                height=25,
                fg_color="#3A2020",
                hover_color="#5A2929",
                command=lambda target=index: _clear_banner_slot(app, target),
            ).grid(row=0, column=1, padx=(3, 0), sticky="ew")

            for widget in (card, image_label):
                widget.bind(
                    "<Button-1>",
                    lambda _event, selected=item: _select_favorite_banner(app, selected),
                )

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
