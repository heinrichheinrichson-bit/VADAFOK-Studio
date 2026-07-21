import unittest
import tempfile
from pathlib import Path

from vadafok_studio.core import batch_engine


class BatchEngineTests(unittest.TestCase):
    def test_analyze_columns_reports_matches_and_ignored_metadata(self):
        matched, ignored = batch_engine.analyze_columns(
            [{"Date": "Friday", "Output Name": "show", "Notes": "live"}],
            [{"name": "date"}],
        )
        self.assertEqual(matched, ["Date"])
        self.assertEqual(ignored, ["Notes"])

    def test_output_column_matching_is_case_and_separator_insensitive(self):
        items = batch_engine.rows_to_batch_items(
            [{"OUTPUT-NAME": "friday_show", "Title": "Live"}],
            "Default",
            [{"name": "title"}],
            "card",
            "Broadcast PNG",
        )
        self.assertEqual(items[0]["output_name"], "friday_show")
        self.assertEqual(items[0]["values"], {"title": "Live"})

    def test_unique_output_name_is_case_insensitive_and_readable(self):
        self.assertEqual(
            batch_engine.unique_output_name("Show", ["show", "Show_2"]),
            "Show_3",
        )

    def test_batch_project_round_trip_uses_clean_valid_file(self):
        items = [{
            "template": "Default",
            "output_name": "show",
            "profile": "Broadcast PNG",
            "values": {"title": "Live"},
        }]
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "show.vbatch"
            batch_engine.save_batch_project_file(path, items)
            self.assertEqual(batch_engine.load_batch_project_file(path), items)
            self.assertFalse(path.with_suffix(".vbatch.tmp").exists())


if __name__ == "__main__":
    unittest.main()
