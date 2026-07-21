from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "vadafok_studio" / "app.py").read_text(encoding="utf-8")
LAYOUT = (ROOT / "vadafok_studio" / "core" / "layout_engine.py").read_text(encoding="utf-8")
PREVIEW = (ROOT / "vadafok_studio" / "card_creator" / "preview.py").read_text(encoding="utf-8")


class CardCreatorLivePreviewPerformanceTests(unittest.TestCase):
    def test_live_preview_uses_short_debounce(self):
        assert "self.after(25, self.card_update_preview)" in APP


    def test_typing_does_not_save_json_on_every_keystroke(self):
        method = APP.split("    def card_preview_changed", 1)[1].split("    def card_clear_values", 1)[0]
        assert "self.after(350, self.card_save_values)" in method
        assert "self.card_save_values()" not in method


    def test_form_uses_stringvar_trace_for_all_value_changes(self):
        assert 'trace_add("write", self.card_preview_changed)' in APP
        method = APP.split('    def card_build_form', 1)[1].split('    def card_save_values', 1)[0]
        assert 'entry.bind("<KeyRelease>"' not in method


    def test_preview_renders_in_memory_without_temp_export_file(self):
        assert "self._render_image(" in PREVIEW
        assert "card_render_to_file(" not in PREVIEW
        assert "Image.open(preview_path)" not in PREVIEW


    def test_layout_engine_exposes_in_memory_renderer(self):
        assert "def render_template_card_image(" in LAYOUT
        assert "img = render_template_card_image(" in LAYOUT
