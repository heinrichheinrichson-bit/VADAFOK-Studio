from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ReleaseTests(unittest.TestCase):
    def test_translation_uses_real_result_field(self):
        text=(ROOT/'vadafok_studio/voice_control/live_card_voice.py').read_text(encoding='utf-8')
        self.assertIn('translated_text', text)
        self.assertNotIn('getattr(result, "text", "")', text)

    def test_commands_use_compact_f8_actions(self):
        text=(ROOT/'vadafok_studio/voice_control/foundation.py').read_text(encoding='utf-8')
        self.assertIn('if command.action == "show":', text)
        self.assertIn('_send_quick_caption_with_existing_action(app)', text)
        self.assertIn('reset_live_card_translation(app)', text)
        self.assertIn('_cancel_quick_caption(app)', text)

    def test_preview_has_minimum_visible_height(self):
        app=(ROOT/'vadafok_studio/quick_caption/window.py').read_text(encoding='utf-8')
        workflow=(ROOT/'vadafok_studio/stream_workflow.py').read_text(encoding='utf-8')
        self.assertIn('app.quick_window.minsize(520, 320)', app)
        self.assertIn('window.minsize(520, 320)', workflow)

if __name__ == '__main__':
    unittest.main()
