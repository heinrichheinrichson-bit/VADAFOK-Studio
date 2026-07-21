from pathlib import Path
import unittest


class CardCreatorResizableWorkspaceTests(unittest.TestCase):
    def test_card_creator_uses_simple_resizable_workspace(self):
        source = Path("vadafok_studio/card_creator/page.py").read_text(encoding="utf-8")
        assert "tk.PanedWindow" in source
        assert "workspace.add(card_pane" in source
        assert "workspace.add(batch_box" in source
        assert "workspace.add(output_pane" in source
        assert "collapse" not in source.lower()
