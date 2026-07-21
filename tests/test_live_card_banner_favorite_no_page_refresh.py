from pathlib import Path
import unittest


class LiveCardBannerFavoriteRefreshTests(unittest.TestCase):
    def test_banner_favorite_selection_does_not_rebuild_live_card_page(self):
        source = Path('vadafok_studio/banner_workflow.py').read_text(encoding='utf-8')
        block = source.split('def _select_favorite_banner', 1)[1].split('def _make_thumbnail', 1)[0]
        assert 'app.show_live_card()' not in block
        assert 'app.update_render_preview()' in block
        assert '_render_banner_favorites(app)' in block
