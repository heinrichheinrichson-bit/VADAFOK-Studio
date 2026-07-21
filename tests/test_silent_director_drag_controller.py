from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from vadafok_studio.silent_director.drag_controller import (
    drag_cancel,
    drag_release,
    drag_target_from_y,
)


ROOT = Path(__file__).resolve().parents[1]


def row(top, height):
    return SimpleNamespace(
        winfo_rooty=lambda: top,
        winfo_height=lambda: height,
    )


def drag_app(**overrides):
    values = dict(
        silent_director_drag_active=True,
        silent_director_drag_index=0,
        silent_director_drop_index=2,
        silent_director_drag_target=2,
        silent_director_dragged_card=Mock(),
        silent_director_action_rows=[],
        silent_director_hide_floating_drop_indicator=Mock(),
        silent_director_drag_target_from_y=Mock(return_value=2),
        silent_director_get_selected_preset=Mock(return_value={"name": "Show"}),
        silent_director_action_button_text=SimpleNamespace(set=Mock()),
        silent_director_edit_index=3,
        silent_director_presets=[],
        silent_director_render_actions_list=Mock(),
        obs_workflow_mark_command=Mock(),
        unbind_all=Mock(),
    )
    values.update(overrides)
    return SimpleNamespace(**values)


class SilentDirectorDragControllerTests(unittest.TestCase):
    def test_app_drag_methods_are_thin_adapters(self):
        source = (ROOT / "vadafok_studio" / "app.py").read_text(encoding="utf-8")
        self.assertIn("return release_silent_director_drag(self, event)", source)
        self.assertIn("return cancel_silent_director_drag(self)", source)
        self.assertNotIn("Exactly one rebuild after release.", source)

    def test_target_positions_include_before_between_and_after_rows(self):
        app = SimpleNamespace(silent_director_action_rows=[row(100, 40), row(160, 40)])

        self.assertEqual(drag_target_from_y(app, 90), 0)
        self.assertEqual(drag_target_from_y(app, 145), 1)
        self.assertEqual(drag_target_from_y(app, 220), 2)

    @patch("vadafok_studio.silent_director.drag_controller.silent_director.move_action_to")
    def test_release_moves_once_and_rebuilds_once(self, move_action_to):
        move_action_to.return_value = [{"name": "Show"}]
        app = drag_app()

        result = drag_release(app)

        self.assertEqual(result, "break")
        move_action_to.assert_called_once_with("Show", 0, 2)
        app.silent_director_render_actions_list.assert_called_once_with()
        self.assertFalse(app.silent_director_drag_active)
        self.assertIsNone(app.silent_director_dragged_card)

    @patch("vadafok_studio.silent_director.drag_controller.silent_director.move_action_to")
    def test_cancel_never_changes_preset_order(self, move_action_to):
        app = drag_app()

        result = drag_cancel(app)

        self.assertEqual(result, "break")
        move_action_to.assert_not_called()
        app.silent_director_render_actions_list.assert_not_called()
        self.assertFalse(app.silent_director_drag_active)


if __name__ == "__main__":
    unittest.main()
