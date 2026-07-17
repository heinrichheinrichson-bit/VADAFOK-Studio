from __future__ import annotations

import unittest

from vadafok_studio.template_editor.refresh_manager import TemplateRefreshManager
from vadafok_studio.template_editor.refresh_profiler import TemplateRefreshProfiler


class _FakeApp:
    def __init__(self):
        self.calls: list[tuple] = []
        self.template_layers_body = object()
        self.template_props_body = object()

    def template_draw_canvas(self, **kwargs):
        self.calls.append(("canvas", kwargs))

    def template_update_fields_overlay(self, **kwargs):
        self.calls.append(("overlay", kwargs))

    def template_build_layers_panel(self):
        self.calls.append(("layers_full",))

    def template_refresh_layers_selection(self):
        self.calls.append(("layers_selection",))

    def template_load_selected_properties(self):
        self.calls.append(("load_properties",))

    def template_build_properties_panel(self):
        self.calls.append(("build_properties",))


class TemplateRefreshChainAnalyzerTests(unittest.TestCase):
    def test_chain_analysis_is_empty_when_profiling_is_disabled(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.selection()

        analysis = manager.refresh_chain_analysis()

        self.assertFalse(analysis["enabled"])
        self.assertEqual(analysis["total_chains"], 0)
        self.assertEqual(analysis["unique_chains"], 0)
        self.assertEqual(analysis["chains"], [])

    def test_identical_selection_chains_are_grouped(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)

        manager.selection()
        manager.selection()

        analysis = manager.refresh_chain_analysis()

        self.assertEqual(analysis["total_chains"], 2)
        self.assertEqual(analysis["unique_chains"], 1)
        chain = analysis["chains"][0]
        self.assertEqual(chain["name"], "selection")
        self.assertEqual(chain["count"], 2)
        self.assertEqual(
            chain["gateways"],
            ["selection", "properties", "overlay", "layers_selection"],
        )
        self.assertEqual(
            chain["structure"],
            [
                {"depth": 0, "name": "selection"},
                {"depth": 1, "name": "properties"},
                {"depth": 1, "name": "overlay"},
                {"depth": 1, "name": "layers_selection"},
            ],
        )
        self.assertGreaterEqual(chain["average_seconds"], 0.0)
        self.assertGreaterEqual(chain["maximum_seconds"], chain["minimum_seconds"])

    def test_different_chain_shapes_remain_separate(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)

        manager.selection(refresh_properties=True)
        manager.selection(refresh_properties=False)

        analysis = manager.refresh_chain_analysis()

        self.assertEqual(analysis["total_chains"], 2)
        self.assertEqual(analysis["unique_chains"], 2)
        signatures = {chain["signature"] for chain in analysis["chains"]}
        self.assertIn(
            "0:selection>1:properties>1:overlay>1:layers_selection",
            signatures,
        )
        self.assertIn(
            "0:selection>1:overlay>1:layers_selection",
            signatures,
        )

    def test_groups_are_sorted_by_frequency_then_total_time(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)

        manager.canvas()
        manager.overlay()
        manager.canvas()

        analysis = manager.refresh_chain_analysis()

        self.assertEqual(
            [chain["name"] for chain in analysis["chains"]],
            ["canvas", "overlay"],
        )
        self.assertEqual(analysis["chains"][0]["count"], 2)

    def test_failed_chains_are_counted(self):
        profiler = TemplateRefreshProfiler(enabled=True)

        def fail():
            raise RuntimeError("expected")

        with self.assertRaisesRegex(RuntimeError, "expected"):
            profiler.run("failure", fail)

        chain = profiler.chain_analysis_snapshot()["chains"][0]
        self.assertEqual(chain["count"], 1)
        self.assertEqual(chain["failed_count"], 1)

    def test_chain_analysis_snapshot_is_detached(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.canvas()

        first = manager.refresh_chain_analysis()
        first["chains"][0]["structure"][0]["name"] = "changed"
        first["chains"][0]["gateways"][0] = "changed"

        second = manager.refresh_chain_analysis()
        self.assertEqual(second["chains"][0]["structure"][0]["name"], "canvas")
        self.assertEqual(second["chains"][0]["gateways"][0], "canvas")

    def test_reset_analysis_clears_chain_groups_but_keeps_metrics(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.canvas()

        manager.reset_analysis()

        self.assertEqual(manager.refresh_chain_analysis()["chains"], [])
        self.assertEqual(
            manager.refresh_profile()["metrics"]["canvas"]["count"],
            1,
        )

    def test_chain_text_contains_grouped_structure_and_frequency(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.selection()
        manager.selection()

        text = manager.refresh_chain_text()

        self.assertIn("=== Refresh Chain Analysis ===", text)
        self.assertIn("Eindeutige Ketten: 1", text)
        self.assertIn("selection | 2x", text)
        self.assertIn("  - selection", text)
        self.assertIn("    - properties", text)
        self.assertIn("    - overlay", text)
        self.assertIn("    - layers_selection", text)


if __name__ == "__main__":
    unittest.main()
