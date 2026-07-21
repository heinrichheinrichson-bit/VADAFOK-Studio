import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from vadafok_studio.card_creator.export_controller import CardExportController


class Variable:
    def __init__(self, value):
        self.value = value

    def get(self):
        return self.value


def make_app(output_folder="", ask=False):
    return SimpleNamespace(
        card_output_folder=Variable(output_folder),
        card_batch_output_folder=Variable(output_folder),
        card_output_name=Variable("card_name"),
        card_export_profile=Variable("Broadcast PNG"),
        card_ask_output_location=Variable(ask),
        card_default_output_name=Mock(return_value="default_card"),
    )


class CardExportControllerTests(unittest.TestCase):
    def test_output_path_uses_engine_and_explicit_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            app = make_app()
            engine = Mock()
            engine.export_path.return_value = Path(temporary) / "card_name.png"
            controller = CardExportController(app, engine, Path(temporary))

            result = controller.output_path(final=True, output_dir=temporary)

            self.assertEqual(result, Path(temporary) / "card_name.png")
            engine.export_path.assert_called_once_with(
                Path(temporary), "card_name", "Broadcast PNG", final=True
            )

    def test_final_path_returns_default_without_dialog(self):
        with tempfile.TemporaryDirectory() as temporary:
            expected = Path(temporary) / "card_name.png"
            engine = Mock()
            engine.export_path.return_value = expected
            controller = CardExportController(
                make_app(temporary, ask=False), engine, Path(temporary)
            )

            with patch(
                "vadafok_studio.card_creator.export_controller.filedialog.asksaveasfilename"
            ) as dialog:
                result = controller.choose_final_output_path()

            self.assertEqual(result, expected)
            dialog.assert_not_called()

    def test_cancelled_batch_directory_returns_none(self):
        with tempfile.TemporaryDirectory() as temporary:
            controller = CardExportController(
                make_app(temporary, ask=True), Mock(), Path(temporary)
            )
            with patch(
                "vadafok_studio.card_creator.export_controller.filedialog.askdirectory",
                return_value="",
            ):
                result = controller.choose_batch_output_directory()

            self.assertIsNone(result)
