import json
import unittest
from pathlib import Path


class EnglishCommandReleaseTests(unittest.TestCase):
    def test_voice_library_contains_english_command(self):
        path = Path(__file__).resolve().parents[1] / "vadafok_studio" / "voice_control" / "voice_library.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        aliases = data["commands"]["translate"]
        self.assertIn("vadafok english", aliases)
        self.assertIn("vadafok translate", aliases)

    def test_version_uses_central_semantic_version(self):
        path = Path(__file__).resolve().parents[1] / "vadafok_studio" / "version.py"
        namespace = {}
        exec(path.read_text(encoding="utf-8"), namespace)
        self.assertRegex(namespace["VERSION"], r"^\d+\.\d+\.\d+\.\d+$")

    def test_quick_card_ui_prefers_english(self):
        path = Path(__file__).resolve().parents[1] / "vadafok_studio" / "voice_control" / "quick_card_voice.py"
        text = path.read_text(encoding="utf-8")
        self.assertIn("Sprachbefehl: VADAFOK ENGLISH", text)
        self.assertIn("Vadafok Translate (Alias)", text)


if __name__ == "__main__":
    unittest.main()
