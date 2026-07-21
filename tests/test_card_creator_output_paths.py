from pathlib import Path
from vadafok_studio.core import config

def test_defaults():
    assert config.DEFAULT_CONFIG["card_output_folder"] == ""
    assert config.DEFAULT_CONFIG["card_batch_output_folder"] == ""
    assert config.DEFAULT_CONFIG["card_ask_output_location"] is False

def test_app_wiring():
    source = Path("vadafok_studio/app.py").read_text(encoding="utf-8")
    assert "def card_choose_final_output_path" in source
    assert "def card_choose_batch_output_directory" in source
    assert "output_dir=batch_output_dir" in source

def test_settings_wiring():
    source = Path("vadafok_studio/settings/page.py").read_text(encoding="utf-8")
    assert "Card Creator Output" in source
    assert "card_output_folder" in source
    assert "card_batch_output_folder" in source
    assert "card_ask_output_location" in source
