import unittest
from unittest.mock import Mock, patch

from vadafok_studio.settings.controller import SettingsController


class Variable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


def make_app():
    app = Mock()
    app.config_data = {}
    values = {
        "host": "localhost",
        "port": "4455",
        "password": "secret",
        "scene_name": "Scene",
        "caption_group": "Caption Group",
        "caption_text": "Caption Text",
        "caption_banner_source": "Banner",
        "caption_render_source": "Render",
        "scene_card_source": "Card",
        "duration": "5",
        "project_folder": "C:/VADAFOK",
        "caption_engine": "obs_text",
        "caption_font_family": "Bebas Neue",
        "caption_font_size": 160,
        "caption_text_color": "#FFFFFF",
        "caption_stroke_color": "#000000",
        "caption_stroke_width": 3,
        "caption_render_width": 1600,
        "caption_render_height": 260,
        "caption_uppercase": True,
        "caption_safe_left": 12,
        "caption_safe_right": 12,
        "caption_safe_top": 24,
        "caption_safe_bottom": 24,
        "voice_enabled": True,
        "voice_trigger_phrase": " live card ",
        "voice_culture": " de-DE ",
        "stream_effect_source": " VADAFOK Stream Effect ",
    }
    for name, value in values.items():
        setattr(app, name, Variable(value))
    return app


class SettingsControllerTests(unittest.TestCase):
    def test_save_config_preserves_existing_values_and_normalization(self):
        app = make_app()
        controller = SettingsController(app)

        with patch("vadafok_studio.settings.controller.persist_config") as persist:
            controller.save_config()

        assert app.config_data["caption_font_size"] == 160
        assert app.config_data["caption_uppercase"] is True
        assert app.config_data["voice_trigger_phrase"] == "live card"
        assert app.config_data["voice_culture"] == "de-DE"
        assert app.config_data["stream_effect_source"] == "VADAFOK Stream Effect"
        persist.assert_called_once_with(app.config_data)


    def test_browse_project_folder_saves_only_after_selection(self):
        app = make_app()
        controller = SettingsController(app)
        controller.save_config = Mock()

        with patch(
            "vadafok_studio.settings.controller.filedialog.askdirectory",
            return_value="D:/Studio",
        ):
            controller.browse_project_folder()

        assert app.project_folder.get() == "D:/Studio"
        controller.save_config.assert_called_once_with()
