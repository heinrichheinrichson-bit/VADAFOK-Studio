from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

from vadafok_studio.silent_director.preset_list_view import render_filtered_presets


ROOT = Path(__file__).resolve().parents[1]


class SilentDirectorPresetListViewTests(unittest.TestCase):
    def test_app_delegates_preset_list_rendering(self):
        app_source = (ROOT / "vadafok_studio" / "app.py").read_text(encoding="utf-8")
        view_source = (
            ROOT / "vadafok_studio" / "silent_director" / "preset_list_view.py"
        ).read_text(encoding="utf-8")
        self.assertIn("from .silent_director import render_filtered_presets", app_source)
        self.assertIn("return render_filtered_presets(self, *_args)", app_source)
        self.assertNotIn("No matching presets.", app_source)
        self.assertIn("No matching presets.", view_source)

    @patch("vadafok_studio.silent_director.preset_list_view.ctk.CTkButton")
    @patch("vadafok_studio.silent_director.preset_list_view.ctk.CTkLabel")
    def test_empty_search_result_offers_clear_search(self, label, button):
        frame = Mock()
        frame.winfo_children.return_value = []
        app = SimpleNamespace(
            silent_director_preset_list_frame=frame,
            silent_director_filtered_presets=Mock(return_value=[]),
            silent_director_search_var=SimpleNamespace(get=lambda: "missing"),
            silent_director_clear_search=Mock(),
        )
        render_filtered_presets(app)
        self.assertEqual(label.call_args.kwargs["text"], "No matching presets.")
        self.assertEqual(button.call_args.kwargs["text"], "CLEAR SEARCH")
        self.assertIs(button.call_args.kwargs["command"], app.silent_director_clear_search)


if __name__ == "__main__":
    unittest.main()
