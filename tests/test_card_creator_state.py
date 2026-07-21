import unittest
from pathlib import Path

from vadafok_studio.card_creator.state import CardCreatorState


class CardCreatorStateTests(unittest.TestCase):
    def test_batch_state_has_safe_independent_defaults(self):
        first = CardCreatorState()
        second = CardCreatorState()

        first.batch_items.append({"output_name": "one"})
        first.batch_selected_index = 0
        first.preview_background_cache = object()
        first.preview_background_key = ("background.png", 1)
        first.last_render = Path("render.png")

        self.assertEqual(second.batch_items, [])
        self.assertIsNone(second.batch_selected_index)
        self.assertIsNone(second.preview_background_cache)
        self.assertIsNone(second.preview_background_key)
        self.assertIsNone(second.last_render)
