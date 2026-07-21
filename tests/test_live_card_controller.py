import sys
import types
import unittest
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

sys.modules.setdefault("customtkinter", types.SimpleNamespace())

from vadafok_studio.live_card.controller import LiveCardController
from vadafok_studio.services.sound_service import SoundService


class Variable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


class LiveCardControllerTests(unittest.TestCase):
    @patch("vadafok_studio.live_card.controller.save_config")
    @patch("vadafok_studio.live_card.controller.filedialog.askopenfilename")
    def test_exact_sound_favorite_slot_can_be_replaced_directly(self, dialog, save):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            sound = project / "Sounds" / "New_Sound.wav"
            sound.parent.mkdir()
            sound.write_bytes(b"RIFF")
            dialog.return_value = str(sound)
            app = SimpleNamespace(
                config_data={"sound_favorites": [
                    {"name": f"Favorit {index + 1}", "file": ""}
                    for index in range(4)
                ]},
                project_folder=Variable(str(project)),
                sound_service=SoundService(project, backend=None),
                sound_favorite_buttons=[],
            )
            controller = LiveCardController(app)
            controller._apply_selected_sound_effect = Mock(return_value=True)

            self.assertTrue(controller.replace_sound_favorite(2))

            slot = app.config_data["sound_favorites"][2]
            self.assertEqual(slot["file"], "New_Sound.wav")
            self.assertEqual(slot["name"], "New Sound")
            controller._apply_selected_sound_effect.assert_called_once_with(
                "New_Sound.wav"
            )
            save.assert_called()

    def test_open_quick_caption_delegates_to_compact_window(self):
        app = Mock()
        controller = LiveCardController(app)
        with patch("vadafok_studio.quick_caption.window.open_quick_caption_window", return_value="window") as opener:
            result = controller.open_quick_caption()
        assert result == "window"
        opener.assert_called_once_with(app)


    def test_show_live_card_page_keeps_compatibility_alias(self):
        app = Mock()
        controller = LiveCardController(app)
        controller.show_live_card = Mock(return_value="live")
        assert controller.show_live_card_page() == "live"
        controller.show_live_card.assert_called_once_with()


    def test_pending_live_card_text_is_preserved_until_widget_exists(self):
        app = Mock(spec=[])
        app.live_card_pending_text = ""
        controller = LiveCardController(app)
        controller.live_card_set_message_text("  Hello  ")
        assert app.live_card_pending_text == "Hello"
        assert controller.live_card_get_message_text() == "Hello"
