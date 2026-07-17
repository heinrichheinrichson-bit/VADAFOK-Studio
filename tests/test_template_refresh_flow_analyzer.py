from __future__ import annotations

import unittest
from unittest.mock import patch

from vadafok_studio.template_editor.refresh_manager import TemplateRefreshManager
from vadafok_studio.template_editor.refresh_profiler import TemplateRefreshProfiler


class _FakeApp:
    def __init__(self):
        self.calls: list[tuple] = []
        self.template_layers_body = object()
        self.template_props_body = object()

    def template_draw_canvas(self, **kwargs): self.calls.append(("canvas", kwargs))
    def template_update_fields_overlay(self, **kwargs): self.calls.append(("overlay", kwargs))
    def template_build_layers_panel(self): self.calls.append(("layers_full",))
    def template_refresh_layers_selection(self): self.calls.append(("layers_selection",))
    def template_load_selected_properties(self): self.calls.append(("load_properties",))
    def template_build_properties_panel(self): self.calls.append(("build_properties",))


class TemplateRefreshFlowAnalyzerTests(unittest.TestCase):
    def test_flow_analysis_is_empty_when_profiling_is_disabled(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.selection()
        analysis = manager.refresh_flow_analysis()
        self.assertFalse(analysis["enabled"])
        self.assertEqual(analysis["total_flows"], 0)
        self.assertEqual(analysis["unique_flows"], 0)
        self.assertEqual(analysis["flows"], [])

    def test_selection_flow_contains_complete_ordered_path(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.selection()
        flow = manager.refresh_flow_analysis()["flows"][0]
        self.assertEqual(flow["start"], "selection")
        self.assertEqual(flow["end"], "layers_selection")
        self.assertEqual(flow["gateways"], ["selection", "properties", "overlay", "layers_selection"])
        self.assertEqual(flow["gateway_count"], 4)
        self.assertEqual(flow["maximum_depth"], 1)

    def test_identical_flows_are_grouped(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.selection(); manager.selection()
        analysis = manager.refresh_flow_analysis()
        self.assertEqual(analysis["total_flows"], 2)
        self.assertEqual(analysis["unique_flows"], 1)
        self.assertEqual(analysis["flows"][0]["count"], 2)

    def test_different_flow_shapes_remain_separate(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True)
        manager.selection(refresh_properties=True)
        manager.selection(refresh_properties=False)
        analysis = manager.refresh_flow_analysis()
        self.assertEqual(analysis["unique_flows"], 2)
        self.assertEqual({flow["gateway_count"] for flow in analysis["flows"]}, {3, 4})

    def test_nested_depth_is_reported(self):
        profiler = TemplateRefreshProfiler(enabled=True)
        def child(): profiler.run("grandchild", lambda: None)
        profiler.run("root", lambda: profiler.run("child", child))
        flow = profiler.flow_analysis_snapshot()["flows"][0]
        self.assertEqual(flow["maximum_depth"], 2)
        self.assertEqual(flow["end"], "grandchild")

    def test_timing_statistics_are_aggregated(self):
        profiler = TemplateRefreshProfiler(enabled=True)
        timings = iter([0.0, 0.002, 1.0, 1.004])
        with patch("vadafok_studio.template_editor.refresh_profiler.perf_counter", side_effect=lambda: next(timings)):
            profiler.run("canvas", lambda: None)
            profiler.run("canvas", lambda: None)
        flow = profiler.flow_analysis_snapshot()["flows"][0]
        self.assertAlmostEqual(flow["minimum_seconds"], 0.002)
        self.assertAlmostEqual(flow["maximum_seconds"], 0.004)
        self.assertAlmostEqual(flow["average_seconds"], 0.003)

    def test_failed_flows_are_counted_with_rate(self):
        profiler = TemplateRefreshProfiler(enabled=True)
        with self.assertRaises(RuntimeError):
            profiler.run("failure", lambda: (_ for _ in ()).throw(RuntimeError("expected")))
        flow = profiler.flow_analysis_snapshot()["flows"][0]
        self.assertEqual(flow["failed_count"], 1)
        self.assertEqual(flow["failure_rate"], 1.0)

    def test_flow_snapshot_is_detached(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True); manager.selection()
        first = manager.refresh_flow_analysis()
        first["flows"][0]["gateways"][0] = "changed"
        first["flows"][0]["structure"][0]["name"] = "changed"
        second = manager.refresh_flow_analysis()
        self.assertEqual(second["flows"][0]["gateways"][0], "selection")
        self.assertEqual(second["flows"][0]["structure"][0]["name"], "selection")

    def test_reset_analysis_clears_flows_but_preserves_metrics(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True); manager.selection(); manager.reset_analysis()
        self.assertEqual(manager.refresh_flow_analysis()["flows"], [])
        self.assertEqual(manager.refresh_profile()["metrics"]["selection"]["count"], 1)

    def test_flow_text_contains_summary_path_and_timing(self):
        manager = TemplateRefreshManager(_FakeApp())
        manager.set_profiling(True); manager.selection()
        text = manager.refresh_flow_text()
        self.assertIn("=== Refresh Flow Analysis ===", text)
        self.assertIn("Flows gesamt: 1", text)
        self.assertIn("selection -> layers_selection", text)
        self.assertIn("4 Gateways", text)
        self.assertIn("Ablauf:", text)
        self.assertIn("- properties", text)


if __name__ == "__main__": unittest.main()
