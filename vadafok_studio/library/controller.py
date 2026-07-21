"""Controller for Library-based selection workflows."""

from __future__ import annotations

from typing import Any

from ..core.library import ROOT_FOLDERS, guessed_tags, scan_library_section


class LibraryController:
    """Own transient Library workflow state outside the Library page widgets."""

    TEMPLATE_EDITOR_PAGE = "Template Editor"
    TEMPLATE_SECTION = "Templates"

    def __init__(self, app: Any) -> None:
        self.app = app
        self._return_page: str | None = None
        self._purpose: str | None = None

    @property
    def is_template_background_picker(self) -> bool:
        return (
            self._return_page == self.TEMPLATE_EDITOR_PAGE
            and self._purpose == "template_background"
        )

    def open_template_background_picker(self) -> None:
        """Open the visual Library and activate picker state afterwards."""
        # Build the Library first. It may recreate widgets and reset page-local
        # attributes, but it cannot clear this controller-owned state.
        self.app.show_library()
        self.app.open_library_section(self.TEMPLATE_SECTION)

        self._purpose = "template_background"
        self._return_page = self.TEMPLATE_EDITOR_PAGE

        # Compatibility flags for existing UI text and older helper methods.
        self.app.library_template_background_picker_mode = True
        self.app.library_return_page = self.TEMPLATE_EDITOR_PAGE

        info = getattr(self.app, "library_info", None)
        if info is not None:
            try:
                info.configure(
                    text=(
                        "TEMPLATE BACKGROUND PICKER — Einfacher Klick zeigt "
                        "die Vorschau. Doppelklick oder SHOW / USE übernimmt "
                        "das Bild und kehrt zum Template Editor zurück."
                    )
                )
            except Exception:
                pass

    def complete_template_background_picker(self) -> bool:
        """Clear picker state and report whether a return is required."""
        should_return = self.is_template_background_picker

        self._purpose = None
        self._return_page = None
        self.app.library_template_background_picker_mode = False
        self.app.library_return_page = None

        return should_return

    def cancel_picker(self) -> None:
        self._purpose = None
        self._return_page = None
        self.app.library_template_background_picker_mode = False
        self.app.library_return_page = None

    def open_section(self, section: str) -> None:
        """Open a Library section and load only that section's assets."""
        section = str(section or "").strip()
        if section in {"", "Folder Overview"}:
            self.app.library_section.set("Folder Overview")
            self.app.library_items = []
            self.app.selected_item = None
            self.app.render_library_grid()
            return
        if section not in ROOT_FOLDERS:
            return
        self.app.library_section.set(section)
        self.app.selected_item = None
        self.app.library_items = scan_library_section(
            self.app.project_folder.get(), section,
        )
        self.app.render_library_grid()

    def reload_section(self) -> None:
        section = str(self.app.library_section.get() or "").strip()
        if section in {"", "All", "Folder Overview"}:
            self.app.library_items = []
            self.app.render_library_folder_overview()
            return
        self.app.library_items = scan_library_section(
            self.app.project_folder.get(), section,
        )
        self.app.selected_item = None
        self.app.render_library_grid()

    @staticmethod
    def item_key(item: Any) -> str:
        return item.relative

    def item_is_favorite(self, item: Any) -> bool:
        return self.item_key(item) in self.app.asset_meta.get("favorites", [])

    def item_tags(self, item: Any) -> list[str]:
        stored = self.app.asset_meta.get("tags", {}).get(self.item_key(item), [])
        return list(dict.fromkeys(stored + guessed_tags(item)))
