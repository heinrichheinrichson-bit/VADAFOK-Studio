import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class VoiceListenerEnglishCommandTests(unittest.TestCase):
    def test_listener_grammar_contains_english_commands(self):
        text = (
            ROOT / "vadafok_studio" / "tools" / "voice_listener.ps1"
        ).read_text(encoding="utf-8")
        for phrase in (
            '"vadafok english"',
            '"Vadafok English"',
            '"vadafok englisch"',
            '"vadafok translate"',
            '"vadafok translation"',
        ):
            self.assertIn(phrase, text)

    def test_python_dispatch_contains_same_commands(self):
        text = (
            ROOT / "vadafok_studio" / "voice_control" / "foundation.py"
        ).read_text(encoding="utf-8")
        for phrase in (
            '"vadafok english"',
            '"vadafok englisch"',
            '"vadafok english text"',
            '"vadafok translate"',
            '"vadafok translation"',
        ):
            self.assertIn(phrase, text)

    def test_version(self):
        namespace = {}
        path = ROOT / "vadafok_studio" / "version.py"
        exec(path.read_text(encoding="utf-8"), namespace)
        self.assertEqual(namespace["VERSION"], "2.27.0.5")


if __name__ == "__main__":
    unittest.main()
