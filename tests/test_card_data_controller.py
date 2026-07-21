import unittest
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.card_creator.data_controller import CardDataController
from vadafok_studio.card_creator.state import CardCreatorState


class Variable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


def make_app():
    title = Variable("Current")
    subtitle = Variable("Subtitle")
    app = SimpleNamespace(
        card_selected_template=Variable("Default"),
        card_creator_values={
            "Default": {"title": title, "subtitle": subtitle}
        },
        card_values_plain=lambda: {
            "title": title.get(),
            "subtitle": subtitle.get(),
        },
        card_save_values=Mock(),
        card_update_preview=Mock(),
        card_values_save_job="queued",
        card_saved_values={},
    )
    return app


class CardDataControllerTests(unittest.TestCase):
    def make_controller(self, app, state=None, persist=None):
        return CardDataController(
            app,
            state or CardCreatorState(),
            persist or Mock(),
        )

    def test_clear_records_history_and_clears_values(self):
        app = make_app()
        state = CardCreatorState()

        self.make_controller(app, state).clear_values()

        self.assertEqual(
            state.data_undo_stack,
            [{"title": "Current", "subtitle": "Subtitle"}],
        )
        self.assertEqual(app.card_creator_values["Default"]["title"].get(), "")
        self.assertEqual(app.card_creator_values["Default"]["subtitle"].get(), "")

    def test_undo_and_redo_restore_snapshots(self):
        app = make_app()
        state = CardCreatorState(
            data_undo_stack=[{"title": "Before", "subtitle": "Old"}]
        )
        controller = self.make_controller(app, state)

        controller.undo()
        self.assertEqual(app.card_creator_values["Default"]["title"].get(), "Before")
        self.assertEqual(state.data_redo_stack[0]["title"], "Current")

        controller.redo()
        self.assertEqual(app.card_creator_values["Default"]["title"].get(), "Current")

    def test_duplicate_snapshot_is_not_recorded_twice(self):
        app = make_app()
        state = CardCreatorState()
        controller = self.make_controller(app, state)

        controller.push_history()
        controller.push_history()

        self.assertEqual(len(state.data_undo_stack), 1)

    def test_empty_undo_shows_information(self):
        app = make_app()
        with patch(
            "vadafok_studio.card_creator.data_controller.messagebox.showinfo"
        ) as info:
            self.make_controller(app).undo()

        info.assert_called_once()
        app.card_save_values.assert_not_called()

    def test_values_plain_reads_variables_and_plain_values(self):
        app = make_app()
        app.card_creator_values["Default"]["count"] = 3

        result = self.make_controller(app).values_plain()

        self.assertEqual(
            result,
            {"title": "Current", "subtitle": "Subtitle", "count": "3"},
        )

    def test_save_values_updates_memory_and_persists(self):
        app = make_app()
        persist = Mock()

        self.make_controller(app, persist=persist).save_values()

        self.assertIsNone(app.card_values_save_job)
        self.assertEqual(
            app.card_saved_values["Default"],
            {"title": "Current", "subtitle": "Subtitle"},
        )
        persist.assert_called_once_with(app.card_saved_values)
