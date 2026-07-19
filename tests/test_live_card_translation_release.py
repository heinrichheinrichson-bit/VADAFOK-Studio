import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class LiveCardTranslationReleaseTests(unittest.TestCase):
    def test_version(self):
        ns = {}
        exec((ROOT/'vadafok_studio/version.py').read_text(encoding='utf-8'), ns)
        self.assertEqual(ns['VERSION'], '2.28.0.0')

    def test_live_card_ui_is_inline(self):
        text=(ROOT/'vadafok_studio/app.py').read_text(encoding='utf-8')
        self.assertIn('ENGLISH PREVIEW · VADAFOK ENGLISH TO USE', text)
        self.assertIn('textvariable=self.live_card_translation_var', text)

    def test_live_card_voice_path(self):
        text=(ROOT/'vadafok_studio/voice_control/foundation.py').read_text(encoding='utf-8')
        self.assertIn('app.show_live_card()', text)
        self.assertIn('use_live_card_translation(app)', text)
        self.assertIn('_send_live_card(app)', text)

if __name__ == '__main__': unittest.main()
