import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.caption_engine.controller import CaptionEngineController


class Variable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


def make_app():
    app = SimpleNamespace(
        config_data={}, save_config=Mock(), after=Mock(return_value="job"),
        after_cancel=Mock(), caption_color_favorite_buttons=[],
    )
    values = {
        "engine": "smart_png", "font_family": "Bebas Neue", "font_size": 160,
        "text_color": "#FFFFFF", "stroke_color": "#000000", "stroke_width": 3,
        "render_width": 1600, "render_height": 260, "uppercase": True,
        "safe_left": 12, "safe_right": 12, "safe_top": 24, "safe_bottom": 24,
    }
    for name, value in values.items():
        setattr(app, f"caption_{name}", Variable(value))
    return app


class CaptionEngineControllerTests(unittest.TestCase):
    def test_hex_colors_are_normalized_but_remain_editable(self):
        self.assertEqual(CaptionEngineController.normalize_color("e0aa36"), "#E0AA36")
        self.assertIsNone(CaptionEngineController.normalize_color("#xyzxyz"))

    def test_exactly_four_color_favorites_are_migrated(self):
        app = make_app()
        app.config_data["caption_color_favorites"] = ["#123456"]
        controller = CaptionEngineController(app)

        favorites = controller.color_favorites()

        self.assertEqual(len(favorites), 4)
        self.assertEqual(favorites[0], "#123456")

    def test_preset_updates_layout_and_marks_page_dirty(self):
        app = make_app()
        controller = CaptionEngineController(app)

        controller.apply_preset("Untertitel")

        self.assertEqual(app.caption_font_size.get(), 96)
        self.assertEqual(app.caption_render_height.get(), 220)
        self.assertTrue(controller.dirty)

    def test_invalid_values_are_not_saved(self):
        app = make_app()
        app.caption_text_color.set("not-a-color")
        controller = CaptionEngineController(app)

        with patch("vadafok_studio.caption_engine.controller.messagebox.showwarning"):
            self.assertFalse(controller.save())

        app.save_config.assert_not_called()

    def test_valid_values_are_saved_and_clear_dirty_state(self):
        app = make_app()
        controller = CaptionEngineController(app)
        controller.dirty = True

        self.assertTrue(controller.save())

        app.save_config.assert_called_once_with()
        self.assertFalse(controller.dirty)

    def test_close_can_be_cancelled_when_changes_are_unsaved(self):
        app = make_app()
        controller = CaptionEngineController(app)
        controller.dirty = True

        with patch(
            "vadafok_studio.caption_engine.controller.messagebox.askyesnocancel",
            return_value=None,
        ):
            self.assertFalse(controller.confirm_close())


if __name__ == "__main__":
    unittest.main()
