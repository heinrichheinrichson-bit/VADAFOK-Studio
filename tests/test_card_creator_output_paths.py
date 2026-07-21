from pathlib import Path
import unittest

from vadafok_studio.core import config


class CardCreatorOutputPathTests(unittest.TestCase):
    def test_defaults(self):
        assert config.DEFAULT_CONFIG["card_output_folder"] == ""
        assert config.DEFAULT_CONFIG["card_batch_output_folder"] == ""
        assert config.DEFAULT_CONFIG["card_ask_output_location"] is False

    def test_app_wiring(self):
        source = Path("vadafok_studio/app.py").read_text(encoding="utf-8")
        batch_source = Path(
            "vadafok_studio/card_creator/batch_controller.py"
        ).read_text(encoding="utf-8")
        assert "def card_choose_final_output_path" in source
        assert "def card_choose_batch_output_directory" in source
        assert "self.card_batch_controller.render()" in source
        assert "output_dir=output_directory" in batch_source
        assert "return self.card_export_controller.render_final()" in source

    def test_settings_wiring(self):
        source = Path("vadafok_studio/settings/page.py").read_text(encoding="utf-8")
        assert "Card Creator Output" in source
        assert "card_output_folder" in source
        assert "card_batch_output_folder" in source
        assert "card_ask_output_location" in source
