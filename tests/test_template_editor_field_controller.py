import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.template_editor import field_controller


class TemplateEditorFieldControllerTests(unittest.TestCase):
    def make_app(self, template):
        ids = iter(["copy-1", "group-copy"])
        return SimpleNamespace(
            template_current=Mock(return_value=template),
            template_push_history=Mock(),
            template_selected_fields=set(),
            template_selected_field=None,
            template_canvas_design_size=(1280, 720),
            template_new_id=Mock(side_effect=lambda: next(ids)),
            template_selected_name="Template",
            template_load_selected_properties=Mock(),
            template_draw_canvas=Mock(),
            template_build_properties_panel=Mock(),
            template_is_field_locked=Mock(return_value=False),
            template_clean_groups=Mock(),
            template_clear_selection=Mock(),
        )

    @patch.object(field_controller.messagebox, "showwarning")
    def test_copy_without_selection_does_not_create_undo_entry(self, warning):
        app = self.make_app({"fields": [], "groups": []})
        field_controller.copy_fields(app)
        app.template_push_history.assert_not_called()
        warning.assert_called_once()

    @patch.object(field_controller, "save_template")
    def test_copy_offsets_field_and_recreates_complete_group(self, save):
        template = {
            "fields": [{
                "id": "source", "name": "title", "x": 1270, "y": 710,
                "width": 100, "height": 50,
            }],
            "groups": [{
                "id": "group", "name": "Header", "field_ids": ["source"],
                "locked": False, "hidden": False,
            }],
        }
        app = self.make_app(template)
        app.template_selected_field = 0
        field_controller.copy_fields(app)
        copied = template["fields"][1]
        self.assertEqual(copied["name"], "title_copy")
        self.assertEqual((copied["x"], copied["y"]), (1180, 670))
        self.assertEqual(template["groups"][1]["field_ids"], ["copy-1"])
        app.template_push_history.assert_called_once_with("copy field")
        save.assert_called_once_with("Template", template)

    @patch.object(field_controller.messagebox, "askyesno", return_value=False)
    def test_cancelled_multi_delete_does_not_create_undo_entry(self, _ask):
        template = {"fields": [{"name": "a"}, {"name": "b"}], "groups": []}
        app = self.make_app(template)
        app.template_selected_fields = {0, 1}
        field_controller.delete_fields(app)
        app.template_push_history.assert_not_called()
        self.assertEqual(len(template["fields"]), 2)


if __name__ == "__main__":
    unittest.main()
