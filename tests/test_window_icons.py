import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from vadafok_studio.core import window_icon


class WindowIconTests(unittest.TestCase):
    def test_window_reuses_owner_icon_and_sets_windows_ico(self):
        photo = object()
        owner = SimpleNamespace(_vadafok_icon_photo=photo)
        window = Mock()
        window.after = Mock()
        window_icon.apply_window_icon(window, owner)
        window.iconbitmap.assert_called_once_with(str(window_icon.ICO_PATH))
        window.iconphoto.assert_called_once_with(False, photo)
        self.assertIs(window._vadafok_icon_photo, photo)
        self.assertEqual(window.after.call_count, 2)

    def test_owner_icon_is_found_through_parent_chain(self):
        photo = object()
        root = SimpleNamespace(_vadafok_icon_photo=photo, master=None)
        child = SimpleNamespace(master=root)
        self.assertIs(window_icon._owner_icon(child), photo)


if __name__ == "__main__":
    unittest.main()
