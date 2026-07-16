from __future__ import annotations

import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch

from vadafok_studio.core import recent_templates


class RecentTemplatesTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.history_path = Path(self.temp_dir.name) / "recent.json"
        self.path_patch = patch.object(recent_templates, "RECENT_TEMPLATES_PATH", self.history_path)
        self.data_patch = patch.object(recent_templates, "DATA_DIR", self.history_path.parent)
        self.path_patch.start()
        self.data_patch.start()

    def tearDown(self) -> None:
        self.data_patch.stop()
        self.path_patch.stop()
        self.temp_dir.cleanup()

    def test_new_template_moves_to_front_without_duplicates(self) -> None:
        available = ["A", "B", "C"]
        recent_templates.record_recent_template("A", available)
        recent_templates.record_recent_template("B", available)
        recent = recent_templates.record_recent_template("A", available)
        self.assertEqual(recent, ["A", "B"])

    def test_history_is_limited_to_ten_entries(self) -> None:
        available = [f"Template {index}" for index in range(12)]
        for name in available:
            recent_templates.record_recent_template(name, available)
        recent = recent_templates.load_recent_templates(available)
        self.assertEqual(len(recent), 10)
        self.assertEqual(recent[0], "Template 11")

    def test_history_survives_reload(self) -> None:
        available = ["Stream Plan", "Schedule"]
        recent_templates.record_recent_template("Stream Plan", available)
        recent_templates.record_recent_template("Schedule", available)
        self.assertEqual(
            recent_templates.load_recent_templates(available),
            ["Schedule", "Stream Plan"],
        )

    def test_stale_templates_are_filtered(self) -> None:
        recent_templates.save_recent_templates(["Deleted", "Existing"])
        self.assertEqual(
            recent_templates.load_recent_templates(["Existing"]),
            ["Existing"],
        )


if __name__ == "__main__":
    unittest.main()
