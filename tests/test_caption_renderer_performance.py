from __future__ import annotations

import ast
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RENDERER_PATH = ROOT / "vadafok_studio" / "core" / "caption_renderer.py"
APP_PATH = ROOT / "vadafok_studio" / "app.py"


class CaptionRendererPerformanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.renderer_source = RENDERER_PATH.read_text(encoding="utf-8")
        cls.app_source = APP_PATH.read_text(encoding="utf-8")
        cls.renderer_tree = ast.parse(cls.renderer_source)
        cls.app_tree = ast.parse(cls.app_source)

    def test_renderer_has_font_and_banner_caches(self) -> None:
        self.assertIn("_FONT_CACHE", self.renderer_source)
        self.assertIn("_FONT_PATH_CACHE", self.renderer_source)
        self.assertIn("_BANNER_CACHE", self.renderer_source)

    def test_banner_cache_invalidates_by_mtime_and_size(self) -> None:
        self.assertIn("st_mtime_ns", self.renderer_source)
        self.assertIn("st_size", self.renderer_source)

    def test_render_function_accepts_profiler(self) -> None:
        function = next(
            node for node in self.renderer_tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "render_caption_png"
        )
        self.assertIn("profiler", [argument.arg for argument in function.args.args])

    def test_renderer_profiles_critical_stages(self) -> None:
        for marker in (
            "Banner load requested",
            "Font fit requested",
            "Text draw requested",
            "PNG save requested",
        ):
            self.assertIn(marker, self.renderer_source)

    def test_app_passes_show_profiler_into_renderer(self) -> None:
        self.assertIn("def render_smart_caption(self, text, profiler=None):", self.app_source)
        self.assertIn("profiler=profiler", self.app_source)
        self.assertIn("self.render_smart_caption(text, profiler=profiler)", self.app_source)


if __name__ == "__main__":
    unittest.main()
