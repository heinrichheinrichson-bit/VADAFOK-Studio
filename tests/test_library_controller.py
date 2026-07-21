from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

from vadafok_studio.library.controller import LibraryController


class LibraryControllerTests(unittest.TestCase):
    def test_picker_state_is_enabled_after_library_build(self) -> None:
        app = MagicMock()
        controller = LibraryController(app)

        controller.open_template_background_picker()

        app.show_library.assert_called_once()
        app.open_library_section.assert_called_once_with("Templates")
        self.assertTrue(controller.is_template_background_picker)
        self.assertTrue(app.library_template_background_picker_mode)
        self.assertEqual(app.library_return_page, "Template Editor")

    def test_complete_returns_true_and_clears_state(self) -> None:
        app = MagicMock()
        controller = LibraryController(app)
        controller.open_template_background_picker()

        self.assertTrue(controller.complete_template_background_picker())
        self.assertFalse(controller.is_template_background_picker)
        self.assertFalse(app.library_template_background_picker_mode)
        self.assertIsNone(app.library_return_page)

    def test_normal_library_state_does_not_request_return(self) -> None:
        app = MagicMock()
        controller = LibraryController(app)

        self.assertFalse(controller.complete_template_background_picker())

    @patch("vadafok_studio.library.controller.scan_library_section")
    def test_open_section_loads_only_selected_folder(self, scan) -> None:
        app = MagicMock()
        app.project_folder.get.return_value = "project"
        scan.return_value = ["asset"]
        controller = LibraryController(app)

        controller.open_section("Banners")

        scan.assert_called_once_with("project", "Banners")
        self.assertEqual(app.library_items, ["asset"])
        app.render_library_grid.assert_called_once()

    @patch("vadafok_studio.library.controller.scan_library_section")
    def test_folder_overview_never_scans_assets(self, scan) -> None:
        app = MagicMock()
        controller = LibraryController(app)

        controller.open_section("Folder Overview")

        scan.assert_not_called()
        self.assertEqual(app.library_items, [])
        self.assertIsNone(app.selected_item)


if __name__ == "__main__":
    unittest.main()
