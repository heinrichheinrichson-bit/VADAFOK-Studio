import unittest

from vadafok_studio.card_creator.state import CardCreatorState


class CardCreatorStateTests(unittest.TestCase):
    def test_batch_state_has_safe_independent_defaults(self):
        first = CardCreatorState()
        second = CardCreatorState()

        first.batch_items.append({"output_name": "one"})
        first.batch_selected_index = 0

        self.assertEqual(second.batch_items, [])
        self.assertIsNone(second.batch_selected_index)
