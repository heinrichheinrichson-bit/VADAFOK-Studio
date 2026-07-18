import tempfile
import unittest
from pathlib import Path

from vadafok_studio.core.config import DEFAULT_CONFIG
from vadafok_studio.services.sound_effect_selection import (
    effect_display_name,
    portable_effect_path,
)
from vadafok_studio.services.sound_service import SoundService


class LiveCardSoundEffectGuiTests(unittest.TestCase):
    def test_default_config_contains_portable_sound_setting(self):
        self.assertIn("selected_sound_effect", DEFAULT_CONFIG)
        self.assertEqual(DEFAULT_CONFIG["selected_sound_effect"], "")

    def test_effect_display_name(self):
        self.assertEqual(effect_display_name("Chat/Ding.wav"), "Ding.wav")
        self.assertEqual(effect_display_name(""), "Kein Effekt ausgewählt")

    def test_portable_effect_path_is_relative_to_sounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            sound = project / "Sounds" / "Chat" / "Ding.wav"
            sound.parent.mkdir(parents=True)
            sound.write_bytes(b"RIFF")
            service = SoundService(project, backend=None)
            self.assertEqual(portable_effect_path(service, sound), "Chat/Ding.wav")

    def test_portable_effect_path_rejects_file_outside_sounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp)
            outside = project / "Ding.wav"
            outside.write_bytes(b"RIFF")
            (project / "Sounds").mkdir()
            service = SoundService(project, backend=None)
            self.assertIsNone(portable_effect_path(service, outside))


if __name__ == "__main__":
    unittest.main()
