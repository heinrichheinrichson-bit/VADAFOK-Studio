from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from vadafok_studio.silent_director.support_controller import (
    director_log_add,
    director_set_status,
    silent_director_filtered_presets,
    silent_director_format_duration,
    silent_director_preset_icon,
    silent_director_preset_stats,
)


ROOT = Path(__file__).resolve().parents[1]


class Variable:
    def __init__(self, value=None):
        self.value = value

    def get(self):
        return self.value

    def set(self, value):
        self.value = value


class SilentDirectorSupportControllerTests(unittest.TestCase):
    def test_all_director_methods_in_app_are_thin_adapters(self):
        import ast

        source = (ROOT / "vadafok_studio" / "app.py").read_text(encoding="utf-8")
        tree = ast.parse(source)
        large = [
            node.name
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef)
            and (
                node.name.startswith("silent_director_")
                or node.name.startswith("director_")
            )
            and node.end_lineno - node.lineno + 1 > 2
        ]
        self.assertEqual(large, [])

    @patch("vadafok_studio.silent_director.support_controller.datetime.datetime")
    def test_log_entries_receive_timestamp_and_are_forwarded(self, datetime_type):
        datetime_type.now.return_value.strftime.return_value = "12:34:56"
        app = SimpleNamespace(
            director_log_entries=[],
            director_log_text_var=Variable(),
            obs_workflow_log=Mock(),
        )

        director_log_add(app, "Started")

        self.assertEqual(app.director_log_entries, ["12:34:56  Started"])
        self.assertEqual(app.director_log_text_var.get(), "12:34:56  Started")
        app.obs_workflow_log.assert_called_once_with("Director: Started")

    def test_status_calculates_bounded_progress_fraction(self):
        app = SimpleNamespace(
            director_status_var=Variable(),
            director_current_action_var=Variable(),
            director_progress_var=Variable(),
            director_progress_percent_var=Variable(),
            update_idletasks=Mock(),
        )

        director_set_status(app, "RUNNING", "Action", "3 / 4")

        self.assertEqual(app.director_progress_percent_var.get(), 0.75)

    def test_stats_and_duration_handle_wait_values(self):
        preset = {
            "actions": [
                {"type": "wait", "seconds": "2,5"},
                {"type": "wait", "seconds": "invalid"},
                {"type": "switch_scene"},
            ]
        }
        self.assertEqual(silent_director_preset_stats(None, preset), (3, 2.5))
        self.assertEqual(silent_director_format_duration(None, 62.5), "1 min 2.5 s")

    def test_filter_prioritizes_favorites_then_name(self):
        app = SimpleNamespace(
            silent_director_search_var=Variable("show"),
            silent_director_favorites_only=Variable(False),
            silent_director_presets=[
                {"name": "Show Zebra", "favorite": False},
                {"name": "Show Alpha", "favorite": True},
                {"name": "Other", "favorite": True},
            ],
        )
        self.assertEqual(
            [item["name"] for item in silent_director_filtered_presets(app)],
            ["Show Alpha", "Show Zebra"],
        )

    def test_icon_respects_explicit_value_and_auto_rules(self):
        self.assertEqual(silent_director_preset_icon(None, {"icon": "MIC"}), "MIC")
        self.assertEqual(
            silent_director_preset_icon(None, {"name": "Boss Fight", "icon": "AUTO"}),
            "GME",
        )


if __name__ == "__main__":
    unittest.main()
