from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_PATH = ROOT / "vadafok_studio" / "app.py"
PAGE_PATH = ROOT / "vadafok_studio" / "settings" / "page.py"


def test_settings_page_is_owned_by_settings_module():
    app_source = APP_PATH.read_text(encoding="utf-8")
    page_source = PAGE_PATH.read_text(encoding="utf-8")

    assert "from vadafok_studio.settings.page import show_settings_page" in app_source
    assert "return show_settings_page(self)" in app_source
    assert "Voice Trigger — Quick Caption" not in app_source
    assert "Voice Trigger — Quick Caption" in page_source


def test_live_card_voice_still_targets_quick_caption():
    page_source = PAGE_PATH.read_text(encoding="utf-8")
    app_source = APP_PATH.read_text(encoding="utf-8")

    assert "command=app.test_voice_trigger" in page_source
    assert "self.open_quick_caption()" in app_source
