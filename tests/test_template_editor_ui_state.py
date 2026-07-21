import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from vadafok_studio.template_editor.ui_state import refresh_toolbar_state


class TemplateEditorToolbarStateTests(unittest.TestCase):
    def make_app(self, selected, locked=(), groups=()):
        buttons = {
            key: Mock() for key in
            ("copy", "delete", "group", "ungroup", "undo", "redo")
        }
        buttons.update({
            "align": [Mock(), Mock()],
            "distribute": [Mock(), Mock()],
            "equal_spacing": [Mock(), Mock()],
        })
        fields = [{"id": f"f{index}"} for index in range(3)]
        return SimpleNamespace(
            template_action_buttons=buttons,
            template_current=Mock(return_value={"fields": fields}),
            template_selected_fields=set(selected),
            template_selected_field=next(iter(selected), None),
            template_is_field_locked=Mock(side_effect=lambda index: index in locked),
            template_field_id=Mock(side_effect=lambda index: f"f{index}"),
            template_groups=Mock(return_value=list(groups)),
            template_undo_stack=[{"before": True}],
            template_redo_stack=[],
            template_selection_summary_label=Mock(),
        )

    def state_for(self, button):
        return button.configure.call_args_list[0].kwargs["state"]

    def test_no_selection_disables_selection_actions(self):
        app = self.make_app(set())
        refresh_toolbar_state(app)
        self.assertEqual(self.state_for(app.template_action_buttons["copy"]), "disabled")
        self.assertEqual(self.state_for(app.template_action_buttons["delete"]), "disabled")
        self.assertEqual(self.state_for(app.template_action_buttons["undo"]), "normal")
        self.assertEqual(self.state_for(app.template_action_buttons["redo"]), "disabled")

    def test_three_unlocked_fields_enable_layout_actions(self):
        app = self.make_app({0, 1, 2})
        refresh_toolbar_state(app)
        for action in ("align", "distribute", "equal_spacing", "group"):
            buttons = app.template_action_buttons[action]
            if not isinstance(buttons, list):
                buttons = [buttons]
            self.assertTrue(all(self.state_for(button) == "normal" for button in buttons))

    def test_locked_selection_disables_delete_and_reports_lock(self):
        app = self.make_app({1}, locked={1})
        refresh_toolbar_state(app)
        self.assertEqual(self.state_for(app.template_action_buttons["copy"]), "normal")
        self.assertEqual(self.state_for(app.template_action_buttons["delete"]), "disabled")
        summary = app.template_selection_summary_label.configure.call_args.kwargs["text"]
        self.assertIn("🔒 1", summary)


if __name__ == "__main__":
    unittest.main()
