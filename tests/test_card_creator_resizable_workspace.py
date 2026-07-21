from pathlib import Path


def test_card_creator_uses_simple_resizable_workspace():
    source = Path("vadafok_studio/card_creator/page.py").read_text(encoding="utf-8")
    assert "tk.PanedWindow" in source
    assert "workspace.add(card_pane" in source
    assert "workspace.add(batch_box" in source
    assert "workspace.add(output_pane" in source
    assert "collapse" not in source.lower()
    assert "sash_place" not in source
