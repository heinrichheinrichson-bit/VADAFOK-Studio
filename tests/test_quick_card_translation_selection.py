import unittest
from types import SimpleNamespace
from unittest.mock import patch

from vadafok_studio.voice_control.quick_card_voice import (
    use_translated_voice_quick_card_text,
)


class FakeWindow:
    def winfo_exists(self):
        return True


class TranslationSelectionTests(unittest.TestCase):
    def test_translate_uses_prepared_text(self):
        selected = []
        app = SimpleNamespace(
            voice_quick_card_window=FakeWindow(),
            voice_quick_card_translation="Thanks for the tip!",
            voice_quick_card_finish=lambda text, status: selected.append((text, status)),
        )
        self.assertTrue(use_translated_voice_quick_card_text(app))
        self.assertEqual(selected[0][0], "Thanks for the tip!")
        self.assertIn("VADAFOK SHOW", selected[0][1])

    def test_translate_rejected_when_not_ready(self):
        app = SimpleNamespace(
            voice_quick_card_window=FakeWindow(),
            voice_quick_card_translation="",
            voice_quick_card_finish=lambda *_: None,
        )
        self.assertFalse(use_translated_voice_quick_card_text(app))

    def test_translate_rejected_without_result_window(self):
        app = SimpleNamespace(
            voice_quick_card_window=None,
            voice_quick_card_translation="Thanks",
            voice_quick_card_finish=lambda *_: None,
        )
        self.assertFalse(use_translated_voice_quick_card_text(app))


if __name__ == "__main__":
    unittest.main()
