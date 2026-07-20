import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class F8LiveCardTranslationReleaseTests(unittest.TestCase):
    def test_version(self):
        namespace = {}
        exec((ROOT / "vadafok_studio/version.py").read_text(encoding="utf-8"), namespace)
        self.assertRegex(namespace["VERSION"], r"^\d+\.\d+\.\d+\.\d+$")

    def test_wake_command_opens_compact_window(self):
        text = (ROOT / 'vadafok_studio/voice_control/foundation.py').read_text(encoding='utf-8')
        start = text.index('if trigger and normalized == trigger:')
        end = text.index('# Voice Quick Card', start)
        block = text[start:end]
        self.assertIn('app.open_quick_caption()', block)
        self.assertNotIn('app.show_live_card()', block)

    def test_f8_contains_english_preview(self):
        text = (ROOT / 'vadafok_studio/quick_caption/window.py').read_text(encoding='utf-8')
        block = text
        self.assertIn('quick_caption_translation_label', block)
        self.assertIn('text="ENGLISH"', block)
        self.assertIn('520x340', block)
        self.assertIn('minsize(520, 320)', block)

    def test_translation_replaces_f8_text(self):
        text = (ROOT / 'vadafok_studio/voice_control/live_card_voice.py').read_text(encoding='utf-8')
        self.assertIn('quick_caption_entry', text)
        self.assertIn('entry.delete("1.0", "end")', text)
        self.assertIn('entry.insert("1.0"', text)


if __name__ == '__main__':
    unittest.main()
