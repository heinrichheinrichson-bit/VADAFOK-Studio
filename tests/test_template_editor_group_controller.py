import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.template_editor import group_controller


class TemplateEditorGroupControllerTests(unittest.TestCase):
    def make_app(self, template, selected):
        field_ids = [field.get("id") for field in template.get("fields", [])]
        return SimpleNamespace(
            template_ensure_field_ids=Mock(),
            template_selected_indices=Mock(return_value=selected),
            template_field_id=Mock(side_effect=lambda index: field_ids[index]),
            template_current=Mock(return_value=template),
            template_groups=Mock(side_effect=lambda: template.get("groups", [])),
            template_clean_groups=Mock(),
            template_push_history=Mock(),
            template_new_id=Mock(return_value="new-group"),
            template_selected_name="Template",
            template_update_fields_overlay=Mock(),
            template_build_layers_panel=Mock(),
        )

    @patch.object(group_controller.messagebox, "showwarning")
    def test_group_requires_two_fields_without_undo_entry(self, warning):
        template = {"fields": [{"id": "a"}], "groups": []}
        app = self.make_app(template, [0])
        group_controller.create_group(app)
        app.template_push_history.assert_not_called()
        warning.assert_called_once()

    @patch.object(group_controller, "save_template")
    def test_group_moves_fields_out_of_previous_groups(self, save):
        template = {
            "fields": [{"id": "a"}, {"id": "b"}, {"id": "c"}],
            "groups": [{"id": "old", "name": "Group", "field_ids": ["a", "c"]}],
        }
        app = self.make_app(template, [0, 1])
        group_controller.create_group(app)
        self.assertEqual(template["groups"][0]["field_ids"], ["c"])
        self.assertEqual(template["groups"][1]["field_ids"], ["a", "b"])
        self.assertEqual(template["groups"][1]["name"], "Group 2")
        app.template_push_history.assert_called_once_with("group fields")
        save.assert_called_once_with("Template", template)


if __name__ == "__main__":
    unittest.main()
