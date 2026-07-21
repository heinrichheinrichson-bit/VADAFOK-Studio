import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.template_editor import history_controller


class TemplateEditorHistoryControllerTests(unittest.TestCase):
    def app(self):
        app = SimpleNamespace()
        app.template_working_data = {"fields": [{"name": "current"}]}
        app.template_current = lambda: app.template_working_data
        app.template_undo_stack = []
        app.template_redo_stack = []
        app.template_undo_reasons = []
        app.template_redo_reasons = []
        app.template_history_limit = 3
        app.template_selected_name = "Template"
        app.template_selected_fields = set()
        app.template_selected_field = None
        app.template_draw_canvas = Mock()
        app.template_load_selected_properties = Mock()
        app.template_refresh_toolbar_state = Mock()
        return app

    def test_push_records_reason_and_clears_redo(self):
        app = self.app()
        app.template_redo_stack = [{"old": True}]
        app.template_redo_reasons = ["old edit"]
        history_controller.push_history(app, "copy field")
        self.assertEqual(app.template_undo_reasons, ["copy field"])
        self.assertEqual(app.template_redo_stack, [])
        self.assertEqual(app.template_redo_reasons, [])

    @patch.object(history_controller, "save_template")
    def test_undo_and_redo_preserve_action_reason(self, _save):
        app = self.app()
        history_controller.push_history(app, "rename field")
        app.template_working_data["fields"][0]["name"] = "renamed"
        history_controller.undo(app)
        self.assertEqual(app.template_working_data["fields"][0]["name"], "current")
        self.assertEqual(app.template_redo_reasons, ["rename field"])
        history_controller.redo(app)
        self.assertEqual(app.template_working_data["fields"][0]["name"], "renamed")
        self.assertEqual(app.template_undo_reasons, ["rename field"])


if __name__ == "__main__":
    unittest.main()
