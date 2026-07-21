import unittest
from types import SimpleNamespace

from vadafok_studio.library.grid_view import filter_library_items


class LibraryGridFilterTests(unittest.TestCase):
    def setUp(self):
        self.image = SimpleNamespace(
            name="Golden Banner.PNG", category="Headers",
            relative="Banners/Golden Banner.PNG",
        )
        self.sound = SimpleNamespace(
            name="Alert.wav", category="Sounds",
            relative="Sounds/Alert.wav",
        )
        self.items = [self.image, self.sound]
        self.tags = {id(self.image): ["Stream", "Gold"], id(self.sound): ["Audio"]}

    def filtered(self, query="", favorites=False):
        return filter_library_items(
            self.items, query, favorites,
            lambda item: item is self.sound,
            lambda item: self.tags[id(item)],
        )

    def test_empty_query_preserves_order(self):
        self.assertEqual(self.filtered(), self.items)

    def test_search_is_case_insensitive_and_includes_tags(self):
        self.assertEqual(self.filtered("GOLD"), [self.image])
        self.assertEqual(self.filtered("audio"), [self.sound])

    def test_favorites_and_search_are_combined(self):
        self.assertEqual(self.filtered("alert", True), [self.sound])
        self.assertEqual(self.filtered("gold", True), [])


if __name__ == "__main__":
    unittest.main()
