import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from vadafok_studio.app import VadafokStudio


class PageCacheNavigationTests(unittest.TestCase):
    def test_cached_silent_director_replaces_current_page(self):
        current = Mock()
        cached = Mock()
        cached.winfo_exists.return_value = True
        app = SimpleNamespace(
            _page_cache={"Silent Director": cached},
            main=current,
            set_active=Mock(),
        )
        builder = Mock()

        VadafokStudio.navigate_to_page(app, "Silent Director", builder)

        current.destroy.assert_called_once_with()
        cached.grid.assert_called_once_with(row=0, column=1, sticky="nsew")
        cached.tkraise.assert_called_once_with()
        app.set_active.assert_called_once_with("Silent Director")
        builder.assert_not_called()

    def test_leaving_silent_director_preserves_its_frame(self):
        silent_page = Mock()
        app = SimpleNamespace(
            _page_cache={},
            main=silent_page,
            active_page="Silent Director",
        )
        replacement = Mock()

        def builder():
            self.assertFalse(hasattr(app, "main"))
            app.main = replacement

        VadafokStudio.navigate_to_page(app, "Settings", builder)

        silent_page.grid_remove.assert_called_once_with()
        self.assertIs(app._page_cache["Silent Director"], silent_page)
        self.assertIs(app.main, replacement)


if __name__ == "__main__":
    unittest.main()
