import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class F8LiveCardTranslationReleaseTests(unittest.TestCase):
    def test_version(self):
        text = (ROOT / 'vadafok_studio/version.py').read_text(encoding='utf-8')
        self.assertIn('VERSION = "2.28.0.1"', text)

    def test_wake_command_opens_compact_window(self):
        text = (ROOT / 'vadafok_studio/voice_control/foundation.py').read_text(encoding='utf-8')
        start = text.index('if trigger and normalized == trigger:')
        end = text.index('# Voice Quick Card', start)
        block = text[start:end]
        self.assertIn('app.open_quick_caption()', block)
        self.assertNotIn('app.show_live_card()', block)

    def test_f8_contains_english_preview(self):
        text = (ROOT / 'vadafok_studio/app.py').read_text(encoding='utf-8')
        start = text.index('def open_quick_caption(self):')
        end = text.index('def ensure_obs_ready', start)
        block = text[start:end]
        self.assertIn('quick_caption_translation_label', block)
        self.assertIn('text="ENGLISH"', block)
        self.assertIn('520x270', block)

    def test_translation_replaces_f8_text(self):
        text = (ROOT / 'vadafok_studio/voice_control/live_card_voice.py').read_text(encoding='utf-8')
        self.assertIn('quick_caption_entry', text)
        self.assertIn('entry.delete("1.0", "end")', text)
        self.assertIn('entry.insert("1.0"', text)


if __name__ == '__main__':
    unittest.main()
