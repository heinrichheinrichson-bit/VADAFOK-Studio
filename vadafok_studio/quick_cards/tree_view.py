"""Incremental tree rendering for Quick Card categories and texts."""

from __future__ import annotations

from typing import Any

import customtkinter as ctk

GOLD = "#D6A43A"
GOLD_DARK = "#8A641D"


def build_quick_cards_tree(app: Any) -> None:
    tree = getattr(app, "quick_cards_tree", None)
    if tree is None:
        return
    scroll_canvas = getattr(tree, "_parent_canvas", None)
    scroll_position = _scroll_position(scroll_canvas)
    for widget in tree.winfo_children():
        widget.destroy()
    app.quick_cards_category_widgets = {}

    for row, category in enumerate(sorted(app.text_library_data)):
        collapsed = category in app.quick_cards_collapsed
        section = ctk.CTkFrame(tree, fg_color="transparent")
        section.grid(row=row, column=0, padx=12, pady=(10, 0), sticky="ew")
        section.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(section, fg_color="#111111", corner_radius=10)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        arrow = ctk.CTkButton(
            header, text="▶" if collapsed else "▼", width=42,
            fg_color="#333333", hover_color="#444444",
            command=lambda selected=category: app.quick_cards_toggle_category(selected),
        )
        arrow.grid(row=0, column=0, padx=(8, 4), pady=8)
        ctk.CTkLabel(
            header, text=category, text_color=GOLD,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).grid(row=0, column=1, padx=4, pady=8, sticky="w")
        ctk.CTkButton(
            header, text="✎", width=42, fg_color="#333333",
            hover_color="#444444",
            command=lambda selected=category: app.quick_cards_rename_category(selected),
        ).grid(row=0, column=2, padx=4, pady=8)
        ctk.CTkButton(
            header, text="LÃ–SCHEN", width=72, fg_color="#5A1F1F",
            hover_color="#7A2A2A",
            command=lambda selected=category: app.quick_cards_delete_category(selected),
        ).grid(row=0, column=3, padx=(4, 8), pady=8)

        body = ctk.CTkFrame(section, fg_color="transparent")
        body.grid(row=1, column=0, sticky="ew")
        body.grid_columnconfigure(0, weight=1)
        app.quick_cards_category_widgets[category] = {
            "arrow": arrow, "body": body, "section": section,
        }
        build_category_body(app, category)
        if collapsed:
            body.grid_remove()

    tree.grid_columnconfigure(0, weight=1)
    _restore_scroll_position(tree, scroll_canvas, scroll_position)


def build_category_body(app: Any, category: str) -> bool:
    """Rebuild only one category's text rows."""
    widgets = getattr(app, "quick_cards_category_widgets", {}).get(category)
    if not widgets:
        return False
    body = widgets["body"]
    for widget in body.winfo_children():
        widget.destroy()
    texts = app.text_library_data.get(category, [])
    if not texts:
        ctk.CTkLabel(body, text="Keine Texte vorhanden.", text_color="#777777").grid(
            row=0, column=0, padx=22, pady=4, sticky="w",
        )
        return True
    for row, text in enumerate(texts):
        _build_text_row(app, body, row, category, text)
    return True


def set_category_collapsed(app: Any, category: str, collapsed: bool) -> bool:
    """Update one category without rebuilding any widgets."""
    widgets = getattr(app, "quick_cards_category_widgets", {}).get(category)
    if not widgets:
        return False
    widgets["arrow"].configure(text="▶" if collapsed else "▼")
    if collapsed:
        widgets["body"].grid_remove()
    else:
        widgets["body"].grid()
    return True


def _build_text_row(
    app: Any, body: Any, row: int, category: str, text: str,
) -> None:
    item = ctk.CTkFrame(body, fg_color="#0B0B0B", corner_radius=8)
    item.grid(row=row, column=0, padx=22, pady=3, sticky="ew")
    item.grid_columnconfigure(0, weight=1)
    editing = (
        app.quick_cards_editing_category == category
        and app.quick_cards_editing_text == text
    )
    if editing:
        entry = ctk.CTkEntry(item, textvariable=app.quick_cards_edit_text_var)
        entry.grid(row=0, column=0, padx=(8, 4), pady=6, sticky="ew")
        entry.focus_set()
        entry.select_range(0, "end")
        entry.bind(
            "<Return>",
            lambda _event, cat=category, old=text: app.quick_cards_commit_text_edit(cat, old),
        )
        entry.bind("<Escape>", lambda _event: app.quick_cards_cancel_text_edit())
        ctk.CTkButton(
            item, text="SPEICHERN", width=76, fg_color=GOLD,
            text_color="#111111", hover_color=GOLD_DARK,
            command=lambda cat=category, old=text: app.quick_cards_commit_text_edit(cat, old),
        ).grid(row=0, column=1, padx=4, pady=6)
        ctk.CTkButton(
            item, text="ABBRECHEN", width=82, fg_color="#333333",
            hover_color="#444444", command=app.quick_cards_cancel_text_edit,
        ).grid(row=0, column=2, padx=(4, 8), pady=6)
        return
    ctk.CTkButton(
        item, text=text, anchor="w", fg_color="#171717",
        hover_color="#2C2C2C", text_color="#D9C58C",
        command=lambda selected=text: app.quick_cards_use_text(selected),
    ).grid(row=0, column=0, padx=(8, 4), pady=6, sticky="ew")
    ctk.CTkButton(
        item, text="✎", width=42, fg_color="#333333",
        hover_color="#444444",
        command=lambda cat=category, old=text: app.quick_cards_start_text_edit(cat, old),
    ).grid(row=0, column=1, padx=4, pady=6)
    ctk.CTkButton(
        item, text="LÃ–SCHEN", width=70, fg_color="#5A1F1F",
        hover_color="#7A2A2A",
        command=lambda cat=category, old=text: app.quick_cards_delete_text(cat, old),
    ).grid(row=0, column=2, padx=(4, 8), pady=6)


def _scroll_position(canvas: Any) -> float:
    try:
        return float(canvas.yview()[0])
    except Exception:
        return 0.0


def _restore_scroll_position(tree: Any, canvas: Any, position: float) -> None:
    if canvas is None or position <= 0:
        return
    try:
        tree.after_idle(lambda: canvas.yview_moveto(position))
    except Exception:
        pass
