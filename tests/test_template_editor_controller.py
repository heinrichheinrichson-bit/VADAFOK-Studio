from __future__ import annotations

import unittest
from unittest.mock import MagicMock

from vadafok_studio.template_editor.controller import TemplateEditorController


class TemplateEditorControllerTests(unittest.TestCase):
    def make_controller(self):
        app = MagicMock()
        loader = MagicMock(return_value={"name": "B", "fields": []})
        controller = TemplateEditorController(app, lambda: ["A", "B"], loader)
        return app, loader, controller

    def test_select_template_updates_editor_state(self):
        app, loader, controller = self.make_controller()

        self.assertTrue(controller.select_template("B"))

        self.assertEqual(app.template_collapsed_groups, set())
        self.assertEqual(app.template_selected_name, "B")
        self.assertIsNone(app.template_selected_field)
        self.assertEqual(app.template_selected_fields, set())
        loader.assert_called_once_with("B")
        self.assertEqual(
            app.template_working_data,
            {"name": "B", "fields": []},
        )
        app.show_template_editor_page.assert_called_once()

    def test_unknown_template_is_ignored(self):
        app, loader, controller = self.make_controller()

        self.assertFalse(controller.select_template("Missing"))

        loader.assert_not_called()
        app.show_template_editor_page.assert_not_called()


if __name__ == "__main__":
    unittest.main()
