from pathlib import Path
import unittest


class CardCreatorResizableWorkspaceTests(unittest.TestCase):
    def test_card_creator_uses_compact_accordion_workspace(self):
        source = Path("vadafok_studio/card_creator/page.py").read_text(encoding="utf-8")
        assert "CardWorkspaceAccordion" in source
        assert 'workspace.add_section("card_data", "Card Data")' in source
        assert 'workspace.add_section("batch_cards", "Batch Cards")' in source
        assert 'workspace.add_section("output", "Output")' in source
        assert 'text="FOCUS PREVIEW"' in source
        assert "left.grid_remove()" in source
        assert "form.grid_remove()" in source
        assert 'text="ZOOM −"' in source
        assert "card_preview_controller.zoom_by" in source
        assert "card_preview_controller.fit" in source
