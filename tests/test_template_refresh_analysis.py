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


class TemplateRefreshAnalysisTests(unittest.TestCase):
    def test_analysis_is_empty_when_profiling_is_disabled(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.canvas()

        analysis = manager.refresh_analysis()

        self.assertFalse(analysis["enabled"])
        self.assertEqual(analysis["total_events"], 0)
        self.assertEqual(analysis["events"], [])
        self.assertEqual(analysis["chains"], [])

    def test_selection_is_reconstructed_as_one_nested_chain(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)

        manager.selection(refresh_properties=True)

        analysis = manager.refresh_analysis()
        self.assertEqual(analysis["total_events"], 4)
        self.assertEqual(len(analysis["chains"]), 1)
        chain = analysis["chains"][0]
        self.assertEqual(chain["name"], "selection")
        self.assertEqual(
            [event["name"] for event in chain["events"]],
            ["selection", "properties", "overlay", "layers_selection"],
        )
        self.assertEqual(
            [event["depth"] for event in chain["events"]],
            [0, 1, 1, 1],
        )
        self.assertEqual(
            analysis["counts"],
            {
                "layers_selection": 1,
                "overlay": 1,
                "properties": 1,
                "selection": 1,
            },
        )

    def test_independent_calls_create_independent_chains(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)

        manager.canvas()
        manager.overlay()

        analysis = manager.refresh_analysis()
        self.assertEqual(
            [chain["name"] for chain in analysis["chains"]],
            ["canvas", "overlay"],
        )

    def test_analysis_snapshot_is_detached(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.canvas()

        first = manager.refresh_analysis()
        first["events"][0]["name"] = "changed"
        first["chains"][0]["events"][0]["name"] = "changed"

        second = manager.refresh_analysis()
        self.assertEqual(second["events"][0]["name"], "canvas")
        self.assertEqual(second["chains"][0]["events"][0]["name"], "canvas")

    def test_reset_analysis_preserves_aggregate_metrics(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.canvas()

        manager.reset_analysis()

        self.assertEqual(manager.refresh_analysis()["total_events"], 0)
        self.assertEqual(
            manager.refresh_profile()["metrics"]["canvas"]["count"],
            1,
        )

    def test_full_profile_reset_clears_metrics_and_analysis(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.canvas()

        manager.reset_profile()

        self.assertEqual(manager.refresh_profile()["metrics"], {})
        self.assertEqual(manager.refresh_analysis()["total_events"], 0)

    def test_failed_gateway_is_visible_and_exception_is_preserved(self):
        profiler = TemplateRefreshProfiler(enabled=True)

        def fail():
            raise RuntimeError("expected")

        with self.assertRaisesRegex(RuntimeError, "expected"):
            profiler.run("failure", fail)

        analysis = profiler.analysis_snapshot()
        self.assertTrue(analysis["events"][0]["failed"])
        self.assertTrue(analysis["chains"][0]["failed"])

    def test_event_limit_is_bounded_and_reports_dropped_events(self):
        profiler = TemplateRefreshProfiler(enabled=True, event_limit=2)

        profiler.run("one", lambda: None)
        profiler.run("two", lambda: None)
        profiler.run("three", lambda: None)

        analysis = profiler.analysis_snapshot()
        self.assertEqual(analysis["total_events"], 2)
        self.assertEqual(analysis["dropped_events"], 1)
        self.assertEqual(
            [event["name"] for event in analysis["events"]],
            ["two", "three"],
        )

    def test_analysis_text_contains_chain_structure(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.selection()

        text = manager.refresh_analysis_text()

        self.assertIn("=== Refresh Analysis ===", text)
        self.assertIn("selection #1", text)
        self.assertIn("  - properties", text)
        self.assertIn("  - overlay", text)
        self.assertIn("  - layers_selection", text)


if __name__ == "__main__":
    unittest.main()
