from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = (ROOT / "vadafok_studio" / "app.py").read_text(encoding="utf-8")
LAYOUT = (ROOT / "vadafok_studio" / "core" / "layout_engine.py").read_text(encoding="utf-8")


def test_live_preview_uses_short_debounce():
    assert "self.after(25, self.card_update_preview)" in APP


def test_typing_does_not_save_json_on_every_keystroke():
    method = APP.split("    def card_preview_changed", 1)[1].split("    def card_clear_values", 1)[0]
    assert "self.after(350, self.card_save_values)" in method
    assert "self.card_save_values()" not in method


def test_form_uses_stringvar_trace_for_all_value_changes():
    assert 'trace_add("write", self.card_preview_changed)' in APP
    method = APP.split('    def card_build_form', 1)[1].split('    def card_save_values', 1)[0]
    assert 'entry.bind("<KeyRelease>"' not in method


def test_preview_renders_in_memory_without_temp_export_file():
    method = APP.split("    def card_update_preview", 1)[1].split("    def card_render_final", 1)[0]
    assert "render_template_card_image(" in method
    assert "card_render_to_file(" not in method
    assert "Image.open(preview_path)" not in method


def test_layout_engine_exposes_in_memory_renderer():
    assert "def render_template_card_image(" in LAYOUT
    assert "img = render_template_card_image(" in LAYOUT
