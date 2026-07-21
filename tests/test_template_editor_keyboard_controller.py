import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from vadafok_studio.template_editor import keyboard_controller


class TemplateEditorKeyboardControllerTests(unittest.TestCase):
    def app(self):
        return SimpleNamespace(
            active_page="Template Editor",
            template_ctrl_down=False,
            template_shift_down=False,
            template_undo=Mock(return_value="undo"),
            template_redo=Mock(),
            template_keyboard_select_all=Mock(),
            template_keyboard_duplicate_selected=Mock(),
            template_keyboard_delete_selected=Mock(),
            template_keyboard_clear_selection=Mock(),
            template_keyboard_move_selected=Mock(return_value="move"),
        )

    def test_shortcuts_are_blocked_outside_template_editor(self):
        app = self.app()
        app.active_page = "Library"
        self.assertFalse(keyboard_controller.shortcuts_allowed(app))

    def test_shortcuts_do_not_steal_keys_from_text_entry(self):
        app = self.app()
        widget = Mock()
        widget.winfo_class.return_value = "Entry"
        event = SimpleNamespace(widget=widget)
        self.assertFalse(keyboard_controller.shortcuts_allowed(app, event))

    def test_shift_arrow_moves_by_ten_pixels(self):
        app = self.app()
        event = SimpleNamespace(keysym="Right", state=0x0001, widget=None)
        self.assertEqual(keyboard_controller.handle_key(app, event), "move")
        app.template_keyboard_move_selected.assert_called_once_with(10, 0)

    def test_control_z_routes_to_undo(self):
        app = self.app()
        event = SimpleNamespace(keysym="z", state=0x0004, widget=None)
        self.assertEqual(keyboard_controller.handle_key(app, event), "undo")
        app.template_undo.assert_called_once()


if __name__ == "__main__":
    unittest.main()
