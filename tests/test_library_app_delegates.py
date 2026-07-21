import unittest

from vadafok_studio.app import VadafokStudio


class LibraryAppDelegateTests(unittest.TestCase):
    def test_grid_callbacks_remain_available_on_app_shell(self):
        for method_name in (
            "item_key",
            "item_is_favorite",
            "item_tags",
            "select_library_item",
            "render_library_grid",
        ):
            with self.subTest(method=method_name):
                self.assertTrue(callable(getattr(VadafokStudio, method_name, None)))


if __name__ == "__main__":
    unittest.main()
