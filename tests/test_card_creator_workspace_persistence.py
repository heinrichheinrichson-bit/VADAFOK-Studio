from pathlib import Path
import unittest


class CardCreatorWorkspacePersistenceTests(unittest.TestCase):
    def test_card_creator_persists_workspace_sashes(self):
        source = Path("vadafok_studio/card_creator/page.py").read_text(encoding="utf-8")
        assert '"card_workspace_sashes"' in source
        assert 'workspace.bind("<ButtonRelease-1>"' in source
        assert "workspace.sash_coord" in source
        assert "workspace.sash_place" in source
        assert "save_config(app.config_data)" in source


    def test_workspace_sash_config_has_safe_default(self):
        source = Path("vadafok_studio/core/config.py").read_text(encoding="utf-8")
        assert '"card_workspace_sashes": []' in source
