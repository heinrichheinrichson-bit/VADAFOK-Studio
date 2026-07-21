import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.template_editor import layout_actions


class TemplateEditorLayoutActionTests(unittest.TestCase):
    def make_app(self, fields, selected):
        template = {"fields": fields}
        return SimpleNamespace(
            template_current=Mock(return_value=template),
            template_selected_unlocked_indices=Mock(return_value=selected),
            template_push_history=Mock(),
            template_selected_name="Template",
            template_draw_canvas=Mock(),
        ), template

    @patch.object(layout_actions.messagebox, "showwarning")
    def test_invalid_alignment_does_not_create_undo_entry(self, warning):
        app, _template = self.make_app([{"x": 10}], [0])
        layout_actions.align_selected(app, "left")
        app.template_push_history.assert_not_called()
        warning.assert_called_once()

    @patch.object(layout_actions, "save_template")
    def test_right_alignment_respects_different_field_widths(self, save):
        fields = [
            {"x": 10, "y": 0, "width": 100, "height": 20},
            {"x": 200, "y": 0, "width": 50, "height": 20},
        ]
        app, template = self.make_app(fields, [0, 1])
        layout_actions.align_selected(app, "right")
        self.assertEqual([field["x"] for field in fields], [150, 200])
        app.template_push_history.assert_called_once_with("align")
        save.assert_called_once_with("Template", template)

    @patch.object(layout_actions, "save_template")
    def test_equal_spacing_accounts_for_field_widths(self, _save):
        fields = [
            {"x": 0, "y": 0, "width": 50, "height": 20},
            {"x": 90, "y": 0, "width": 100, "height": 20},
            {"x": 300, "y": 0, "width": 50, "height": 20},
        ]
        app, _template = self.make_app(fields, [0, 1, 2])
        layout_actions.equal_spacing_selected(app, "horizontal")
        self.assertEqual([field["x"] for field in fields], [0, 125, 300])
        app.template_push_history.assert_called_once_with("equal spacing")


if __name__ == "__main__":
    unittest.main()
