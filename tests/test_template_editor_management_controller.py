import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.template_editor import management_controller


class TemplateEditorManagementControllerTests(unittest.TestCase):
    @patch.object(management_controller, "duplicate_template")
    def test_duplicate_clears_all_field_selection(self, duplicate):
        duplicate.return_value = {"name": "Copy", "fields": []}
        app = SimpleNamespace(
            template_selected_name="Original",
            template_selected_field=2,
            template_selected_fields={1, 2},
            show_template_editor_page=Mock(),
        )
        management_controller.duplicate_current(app)
        self.assertEqual(app.template_selected_name, "Copy")
        self.assertIsNone(app.template_selected_field)
        self.assertEqual(app.template_selected_fields, set())
        app.show_template_editor_page.assert_called_once()

    @patch.object(management_controller, "rename_template")
    def test_unchanged_name_does_not_touch_template_store(self, rename):
        app = SimpleNamespace(
            template_selected_name="Current",
            ask_template_name_dialog=Mock(return_value=" Current "),
        )
        management_controller.rename_current(app)
        rename.assert_not_called()


if __name__ == "__main__":
    unittest.main()
