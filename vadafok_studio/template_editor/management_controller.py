"""Template document management actions."""

from __future__ import annotations

from typing import Any
from tkinter import messagebox

from ..core.template_store import (
    create_template, delete_template, duplicate_template, get_default_template,
    list_templates, load_template, rename_template, set_default_template,
)


def delete_current(app: Any) -> None:
    if not list_templates():
        return
    name = app.template_selected_name
    if not messagebox.askyesno(
        "Template löschen", f"Template wirklich löschen?\n\n{name}",
    ):
        return
    try:
        delete_template(name)
        if (
            hasattr(app, "card_selected_template")
            and app.card_selected_template.get() == name
        ):
            app.card_selected_template.set("")
    except Exception as error:
        messagebox.showerror("Template löschen", str(error))
        return
    names = list_templates()
    if names:
        default_name = get_default_template()
        app.template_selected_name = default_name if default_name in names else names[0]
        app.template_working_data = load_template(app.template_selected_name)
    else:
        data = create_template("Default Stream Plan")
        app.template_selected_name = data["name"]
        app.template_working_data = data
    app.template_selected_field = None
    app.template_selected_fields = set()
    app.show_template_editor_page()


def duplicate_current(app: Any) -> None:
    try:
        data = duplicate_template(app.template_selected_name)
        app.template_selected_name = data["name"]
        app.template_working_data = data
        app.template_selected_field = None
        app.template_selected_fields = set()
        app.show_template_editor_page()
    except Exception as error:
        messagebox.showerror("Template duplizieren", str(error))


def rename_current(app: Any) -> None:
    new_name = app.ask_template_name_dialog(
        "Template umbenennen", app.template_selected_name,
    )
    new_name = str(new_name or "").strip()
    if not new_name or new_name == app.template_selected_name:
        return
    try:
        was_default = get_default_template() == app.template_selected_name
        data = rename_template(app.template_selected_name, new_name)
        app.template_selected_name = data["name"]
        app.template_working_data = data
        if was_default:
            set_default_template(app.template_selected_name)
        app.show_template_editor_page()
    except Exception as error:
        messagebox.showerror("Template umbenennen", str(error))


def set_current_default(app: Any) -> None:
    if not app.template_selected_name:
        return
    set_default_template(app.template_selected_name)
    messagebox.showinfo(
        "Default Template", f"Als Default gesetzt:\n{app.template_selected_name}",
    )
    app.show_template_editor_page()
