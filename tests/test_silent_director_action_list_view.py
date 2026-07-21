from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from vadafok_studio.silent_director.action_list_view import render_actions_list


ROOT = Path(__file__).resolve().parents[1]


class SilentDirectorActionListViewTests(unittest.TestCase):
    def test_app_delegates_action_list_rendering(self):
        source = (ROOT / "vadafok_studio" / "app.py").read_text(encoding="utf-8")
        self.assertIn("from .silent_director import render_actions_list", source)
        self.assertIn("return render_actions_list(self)", source)
        self.assertNotIn("No actions yet. Add one below.", source)

    @patch("vadafok_studio.silent_director.action_list_view.ctk.CTkFrame")
    @patch("vadafok_studio.silent_director.action_list_view.ctk.CTkLabel")
    def test_empty_timeline_renders_hint_and_resets_widget_state(self, label, frame_class):
        child = Mock()
        frame = Mock()
        frame.winfo_children.return_value = [child]
        frame_class.return_value = Mock()
        app = SimpleNamespace(
            silent_director_actions_frame=frame,
            silent_director_action_rows=[Mock()],
            director_action_card_widgets={1: Mock()},
            silent_director_get_selected_preset=Mock(return_value={"actions": []}),
        )

        render_actions_list(app)

        child.destroy.assert_called_once_with()
        self.assertEqual(app.silent_director_action_rows, [])
        self.assertEqual(app.director_action_card_widgets, {})
        self.assertEqual(label.call_args.kwargs["text"], "No actions yet. Add one below.")

    @patch("vadafok_studio.silent_director.action_list_view._render_controls")
    @patch("vadafok_studio.silent_director.action_list_view.ctk.CTkFont")
    @patch("vadafok_studio.silent_director.action_list_view.ctk.CTkButton")
    @patch("vadafok_studio.silent_director.action_list_view.ctk.CTkLabel")
    @patch("vadafok_studio.silent_director.action_list_view.ctk.CTkFrame")
    def test_action_widgets_are_retained_for_runtime_highlighting(
        self, frame_class, label_class, button_class, _font, _controls
    ):
        container = Mock()
        container.winfo_children.return_value = []
        widgets = [Mock() for _ in range(5)]
        frame_class.side_effect = widgets
        badge, drag_handle, detail_label, runtime_label = [Mock() for _ in range(4)]
        label_class.side_effect = [badge, drag_handle, detail_label, runtime_label]
        title_button = Mock()
        button_class.return_value = title_button
        app = SimpleNamespace(
            silent_director_actions_frame=container,
            silent_director_get_selected_preset=Mock(
                return_value={"actions": [{"type": "wait", "seconds": "2"}]}
            ),
            silent_director_timeline_style=Mock(
                return_value={
                    "badge": "TM",
                    "title": "WAIT",
                    "accent": "#6EA6E8",
                    "card": "#16202C",
                }
            ),
            silent_director_timeline_detail=Mock(return_value="2 Sekunden"),
            silent_director_drag_start=Mock(),
            silent_director_edit_action=Mock(),
            director_set_active_action=Mock(),
            director_active_action_index=None,
        )

        render_actions_list(app)

        retained = app.director_action_card_widgets[0]
        self.assertIs(retained["title"], title_button)
        self.assertIs(retained["runtime"], runtime_label)


if __name__ == "__main__":
    unittest.main()
