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


class TemplateRefreshProfilerTests(unittest.TestCase):
    def test_profiling_is_disabled_by_default(self):
        app = _FakeApp()
        manager = TemplateRefreshManager(app)
        manager.canvas(refresh_layers=False)
        self.assertEqual(app.calls, [("canvas", {"refresh_layers": False})])
        self.assertEqual(manager.refresh_profile(), {"enabled": False, "metrics": {}})

    def test_enabled_profiler_counts_gateway_calls(self):
        app = _FakeApp()
        manager = TemplateRefreshManager(app)
        manager.set_profiling(True)
        manager.canvas()
        manager.canvas(refresh_layers=False)
        profile = manager.refresh_profile()
        self.assertTrue(profile["enabled"])
        self.assertEqual(profile["metrics"]["canvas"]["count"], 2)

    def test_profile_contains_non_negative_timing_values(self):
        app = _FakeApp()
        manager = TemplateRefreshManager(app)
        manager.set_profiling(True)
        manager.overlay(refresh_layers=False, refresh_status=False)
        metric = manager.refresh_profile()["metrics"]["overlay"]
        for key in (
            "total_seconds",
            "last_seconds",
            "maximum_seconds",
            "average_seconds",
        ):
            self.assertGreaterEqual(metric[key], 0.0)

    def test_selection_preserves_existing_runtime_order(self):
        app = _FakeApp()
        manager = TemplateRefreshManager(app)
        manager.set_profiling(True)
        manager.selection(refresh_properties=True)
        self.assertEqual(
            app.calls,
            [
                ("load_properties",),
                ("build_properties",),
                (
                    "overlay",
                    {
                        "bg_info": None,
                        "refresh_layers": False,
                        "refresh_status": True,
                    },
                ),
                ("layers_selection",),
            ],
        )
        metrics = manager.refresh_profile()["metrics"]
        self.assertEqual(metrics["selection"]["count"], 1)
        self.assertEqual(metrics["properties"]["count"], 1)
        self.assertEqual(metrics["overlay"]["count"], 1)
        self.assertEqual(metrics["layers_selection"]["count"], 1)

    def test_reset_clears_metrics_without_disabling_profiler(self):
        app = _FakeApp()
        manager = TemplateRefreshManager(app)
        manager.set_profiling(True)
        manager.canvas()
        manager.reset_profile()
        self.assertEqual(manager.refresh_profile(), {"enabled": True, "metrics": {}})

    def test_exceptions_are_not_swallowed(self):
        profiler = TemplateRefreshProfiler(enabled=True)

        def fail():
            raise RuntimeError("expected")

        with self.assertRaisesRegex(RuntimeError, "expected"):
            profiler.run("failure", fail)
        self.assertEqual(profiler.snapshot()["metrics"]["failure"]["count"], 1)


if __name__ == "__main__":
    unittest.main()
