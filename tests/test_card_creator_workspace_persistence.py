from pathlib import Path
import unittest


class CardCreatorWorkspacePersistenceTests(unittest.TestCase):
    def test_card_creator_persists_active_workspace_section(self):
        source = Path("vadafok_studio/card_creator/page.py").read_text(encoding="utf-8")
        assert '"card_workspace_section"' in source
        assert "remember_workspace_section" in source
        assert "save_config(app.config_data)" in source


    def test_workspace_section_config_has_safe_default(self):
        source = Path("vadafok_studio/core/config.py").read_text(encoding="utf-8")
        assert '"card_workspace_section": "card_data"' in source
