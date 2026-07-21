"""Tree rendering for Quick Card categories and texts."""

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
    scroll_position = 0.0
    try:
        scroll_position = float(scroll_canvas.yview()[0])
    except Exception:
        pass
    for widget in tree.winfo_children():
        widget.destroy()
    app.quick_cards_category_widgets = {}

    row = 0
    for category in sorted(app.text_library_data):
        collapsed = category in app.quick_cards_collapsed
        header = ctk.CTkFrame(tree, fg_color="#111111", corner_radius=10)
        header.grid(row=row, column=0, padx=12, pady=(10, 4), sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        arrow_button = ctk.CTkButton(
            header, text="▶" if collapsed else "▼", width=42,
            fg_color="#333333", hover_color="#444444",
            command=lambda selected=category: app.quick_cards_toggle_category(selected),
        )
        arrow_button.grid(row=0, column=0, padx=(8, 4), pady=8)
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
            header, text="DEL", width=54, fg_color="#5A1F1F",
            hover_color="#7A2A2A",
            command=lambda selected=category: app.quick_cards_delete_category(selected),
        ).grid(row=0, column=3, padx=(4, 8), pady=8)
        row += 1
        category_rows = []
        texts = app.text_library_data.get(category, [])
        if not texts:
            empty_label = ctk.CTkLabel(
                tree, text="No texts.", text_color="#777777",
            )
            empty_label.grid(
                row=row, column=0, padx=34, pady=4, sticky="w",
            )
            category_rows.append(empty_label)
            row += 1
        for text in texts:
            row, item = _build_text_row(app, tree, row, category, text)
            category_rows.append(item)
        app.quick_cards_category_widgets[category] = {
            "arrow": arrow_button,
            "rows": category_rows,
        }
        if collapsed:
            for widget in category_rows:
                widget.grid_remove()
    tree.grid_columnconfigure(0, weight=1)
    if scroll_canvas is not None and scroll_position > 0:
        try:
            tree.after_idle(
                lambda position=scroll_position: scroll_canvas.yview_moveto(position)
            )
        except Exception:
            pass


def set_category_collapsed(app: Any, category: str, collapsed: bool) -> bool:
    """Update one category without rebuilding the Quick Cards tree."""
    widgets = getattr(app, "quick_cards_category_widgets", {}).get(category)
    if not widgets:
        return False
    widgets["arrow"].configure(text="▶" if collapsed else "▼")
    for widget in widgets["rows"]:
        if collapsed:
            widget.grid_remove()
        else:
            widget.grid()
    return True


def _build_text_row(
    app: Any, tree: Any, row: int, category: str, text: str,
) -> tuple[int, Any]:
    item = ctk.CTkFrame(tree, fg_color="#0B0B0B", corner_radius=8)
    item.grid(row=row, column=0, padx=34, pady=3, sticky="ew")
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
            item, text="SAVE", width=60, fg_color=GOLD,
            text_color="#111111", hover_color=GOLD_DARK,
            command=lambda cat=category, old=text: app.quick_cards_commit_text_edit(cat, old),
        ).grid(row=0, column=1, padx=4, pady=6)
        ctk.CTkButton(
            item, text="CANCEL", width=70, fg_color="#333333",
            hover_color="#444444", command=app.quick_cards_cancel_text_edit,
        ).grid(row=0, column=2, padx=(4, 8), pady=6)
    else:
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
            item, text="DEL", width=48, fg_color="#5A1F1F",
            hover_color="#7A2A2A",
            command=lambda cat=category, old=text: app.quick_cards_delete_text(cat, old),
        ).grid(row=0, column=2, padx=(4, 8), pady=6)
    return row + 1, item
