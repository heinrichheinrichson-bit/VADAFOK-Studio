from pathlib import Path


def test_back_to_live_card_reloads_library_favorites():
    source = Path('vadafok_studio/live_card/controller.py').read_text(encoding='utf-8')
    block = source.split('def return_to_live_card_from_library', 1)[1].split(
        'def open_template_background_picker', 1
    )[0]
    assert 'app.asset_meta = load_asset_meta()' in block
    assert 'self.show_live_card()' in block


def test_live_card_uses_most_recent_four_banner_favorites():
    source = Path('vadafok_studio/banner_workflow.py').read_text(encoding='utf-8')
    block = source.split('def _load_banner_favorites', 1)[1].split(
        'def _select_favorite_banner', 1
    )[0]
    assert 'reversed(favorite_keys)' in block
    assert '_MAX_FAVORITES' in block
