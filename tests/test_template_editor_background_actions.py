import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.template_editor import background_actions


class TemplateEditorBackgroundActionTests(unittest.TestCase):
    @patch.object(background_actions, "background_path")
    def test_status_checks_resolved_template_background(self, resolve):
        resolved = Mock()
        resolved.exists.return_value = True
        resolve.return_value = resolved
        template = {"background": "background.png"}
        app = SimpleNamespace(
            template_current=Mock(return_value=template),
            template_selected_name="Template",
        )
        self.assertEqual(background_actions.background_status(app), "background.png (OK)")
        resolve.assert_called_once_with("Template", template)

    @patch.object(background_actions.messagebox, "showinfo")
    @patch.object(background_actions.filedialog, "askopenfilename", return_value="")
    def test_cancel_file_dialog_does_not_change_background(self, _dialog, info):
        app = SimpleNamespace(template_set_background_path=Mock())
        background_actions.choose_background_file(app)
        app.template_set_background_path.assert_not_called()
        info.assert_not_called()


if __name__ == "__main__":
    unittest.main()
