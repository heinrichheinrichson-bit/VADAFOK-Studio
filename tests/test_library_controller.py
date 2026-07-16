from __future__ import annotations

import unittest
from unittest.mock import MagicMock

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


if __name__ == "__main__":
    unittest.main()
