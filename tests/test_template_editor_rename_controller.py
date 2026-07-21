import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.template_editor import rename_controller


class TemplateEditorRenameControllerTests(unittest.TestCase):
    @patch.object(rename_controller, "save_template")
    def test_unchanged_name_does_not_create_history_or_save(self, save):
        entry = Mock()
        entry.get.return_value = "title"
        template = {"fields": [{"name": "title"}]}
        app = SimpleNamespace(
            template_rename_entry=entry,
            template_renaming_kind="field",
            template_renaming_target=0,
            template_current=Mock(return_value=template),
            template_push_history=Mock(),
            template_selected_field=0,
            template_selected_name="Template",
            template_build_layers_panel=Mock(),
        )
        rename_controller.commit_inline_rename(app)
        app.template_push_history.assert_not_called()
        save.assert_not_called()
        app.template_build_layers_panel.assert_called_once()


if __name__ == "__main__":
    unittest.main()
