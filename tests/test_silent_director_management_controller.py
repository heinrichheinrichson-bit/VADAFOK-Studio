from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from vadafok_studio.silent_director.management_controller import (
    add_action,
    create_preset,
    duplicate_action,
    get_selected_preset,
    move_action,
)


ROOT = Path(__file__).resolve().parents[1]


class Variable:
    def __init__(self, value=None):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


def action_app(preset):
    return SimpleNamespace(
        silent_director_presets=[preset],
        silent_director_selected=Variable(preset["name"]),
        silent_director_get_selected_preset=Mock(return_value=preset),
        silent_director_action_type=Variable("wait"),
        silent_director_action_scene=Variable(""),
        silent_director_action_source=Variable(""),
        silent_director_action_text=Variable(""),
        silent_director_wait_seconds=Variable("2"),
        silent_director_normalize_wait_seconds=Mock(return_value="2"),
        silent_director_edit_index=None,
        silent_director_action_button_text=Variable("+ ADD ACTION"),
        silent_director_cancel_action_edit=Mock(),
        silent_director_update_action_fields=Mock(),
        silent_director_render_actions_list=Mock(),
        silent_director_refresh_action_cards=Mock(),
        obs_workflow_mark_command=Mock(),
    )


class SilentDirectorManagementControllerTests(unittest.TestCase):
    def test_app_management_methods_are_thin_adapters(self):
        source = (ROOT / "vadafok_studio" / "app.py").read_text(encoding="utf-8")
        self.assertIn("return director_management.add_action(self)", source)
        self.assertIn("return director_management.duplicate_preset(self, preset)", source)
        self.assertNotIn("Silent Director action added: {action_type}", source)

    def test_selected_preset_matches_name_and_falls_back_to_first(self):
        app = SimpleNamespace(
            silent_director_selected=Variable("Second"),
            silent_director_presets=[{"name": "First"}, {"name": "Second"}],
        )
        self.assertEqual(get_selected_preset(app)["name"], "Second")
        app.silent_director_selected.set("Missing")
        self.assertEqual(get_selected_preset(app)["name"], "First")

    @patch("vadafok_studio.silent_director.management_controller.silent_director.add_action")
    def test_wait_action_is_normalized_and_added_once(self, store_add):
        preset = {"name": "Show", "actions": []}
        app = action_app(preset)
        store_add.return_value = [preset]

        add_action(app)

        store_add.assert_called_once_with(
            "Show",
            {"type": "wait", "scene": "", "text": "", "source": "", "seconds": "2"},
        )
        app.silent_director_cancel_action_edit.assert_called_once_with()
        app.silent_director_render_actions_list.assert_called_once_with()

    @patch("vadafok_studio.silent_director.management_controller.silent_director.add_preset")
    @patch("vadafok_studio.silent_director.management_controller.messagebox.showwarning")
    def test_duplicate_preset_name_is_rejected_case_insensitively(self, warning, store_add):
        app = SimpleNamespace(
            silent_director_new_name=Variable("SHOW"),
            silent_director_presets=[{"name": "Show"}],
            obs_workflow_state=SimpleNamespace(current_scene="Main"),
        )

        create_preset(app)

        warning.assert_called_once()
        store_add.assert_not_called()

    @patch("vadafok_studio.silent_director.management_controller.silent_director.duplicate_action")
    def test_duplicate_action_inserts_copy_below_original(self, store_duplicate):
        preset = {
            "name": "Show",
            "actions": [
                {"type": "switch_scene", "scene": "Main"},
                {"type": "wait", "seconds": "2"},
            ],
        }
        app = action_app(preset)
        store_duplicate.return_value = [preset]

        duplicate_action(app, 0)

        store_duplicate.assert_called_once_with("Show", 0)
        self.assertEqual(app.silent_director_edit_index, 1)
        self.assertEqual(app.silent_director_action_button_text.get(), "UPDATE ACTION")

    @patch("vadafok_studio.silent_director.management_controller.silent_director.move_action")
    def test_move_action_refreshes_existing_cards_without_rebuild(self, store_move):
        preset = {"name": "Show", "actions": [{"type": "wait"}]}
        app = action_app(preset)
        store_move.return_value = [preset]

        move_action(app, 0, 1)

        store_move.assert_called_once_with("Show", 0, 1)
        app.silent_director_refresh_action_cards.assert_called_once_with()
        app.silent_director_render_actions_list.assert_not_called()


if __name__ == "__main__":
    unittest.main()
