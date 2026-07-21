"""Compact accordion workspace used by the Card Creator sidebar."""

from __future__ import annotations

from collections.abc import Callable

import customtkinter as ctk


class CardWorkspaceAccordion:
    """Keep every section header visible while one body uses the free height."""

    def __init__(
        self,
        parent,
        *,
        active_key: str,
        on_change: Callable[[str], None] | None = None,
    ) -> None:
        self.frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.frame.grid_columnconfigure(0, weight=1)
        self._requested_key = active_key
        self._active_key: str | None = None
        self._on_change = on_change
        self._sections: dict[str, tuple[ctk.CTkButton, ctk.CTkFrame, int]] = {}

    @property
    def active_key(self) -> str | None:
        return self._active_key

    def add_section(self, key: str, title: str) -> ctk.CTkFrame:
        section_index = len(self._sections)
        header_row = section_index * 2
        body_row = header_row + 1

        header = ctk.CTkButton(
            self.frame,
            text=f"▸  {title}",
            anchor="w",
            height=42,
            corner_radius=10,
            fg_color="#171717",
            hover_color="#242424",
            text_color="#D6A43A",
            font=ctk.CTkFont(size=16, weight="bold"),
            command=lambda selected=key: self.activate(selected),
        )
        header.grid(row=header_row, column=0, sticky="ew", pady=(0, 4))

        body = ctk.CTkFrame(self.frame, fg_color="#0B0B0B", corner_radius=10)
        body.grid(row=body_row, column=0, sticky="nsew", pady=(0, 6))
        body.grid_remove()
        self._sections[key] = (header, body, body_row)

        if key == self._requested_key or (self._active_key is None and section_index == 0):
            self.activate(key, notify=False)
        return body

    def activate(self, key: str, *, notify: bool = True) -> None:
        if key not in self._sections:
            return

        for section_key, (header, body, row) in self._sections.items():
            selected = section_key == key
            self.frame.grid_rowconfigure(row, weight=1 if selected else 0)
            if selected:
                body.grid()
                header.configure(text=f"▾  {header.cget('text')[3:]}", fg_color="#242018")
            else:
                body.grid_remove()
                header.configure(text=f"▸  {header.cget('text')[3:]}", fg_color="#171717")

        changed = self._active_key != key
        self._active_key = key
        if changed and notify and self._on_change is not None:
            self._on_change(key)
