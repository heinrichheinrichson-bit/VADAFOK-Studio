"""Central refresh gateway for the Template Editor.

The manager deliberately contains no rendering logic. It provides one stable
interface around the existing application methods so future controller
extractions can happen without changing user-facing behavior.
"""

from __future__ import annotations

from typing import Any, Callable, TypeVar

from .refresh_profiler import TemplateRefreshProfiler

_Result = TypeVar("_Result")


class TemplateRefreshManager:
    """Coordinate targeted Template Editor refresh operations."""

    def __init__(
        self,
        app: Any,
        profiler: TemplateRefreshProfiler | None = None,
    ) -> None:
        self.app = app
        self.profiler = profiler or TemplateRefreshProfiler(enabled=False)

    def _run(self, name: str, callback: Callable[[], _Result]) -> _Result:
        return self.profiler.run(name, callback)

    def set_profiling(self, enabled: bool) -> None:
        """Enable or disable in-memory refresh measurements."""

        self.profiler.set_enabled(enabled)

    def reset_profile(self) -> None:
        """Clear all collected refresh measurements."""

        self.profiler.reset()

    def refresh_profile(self) -> dict[str, Any]:
        """Return a detached snapshot of the current refresh measurements."""

        return self.profiler.snapshot()

    def refresh_developer_view(self) -> dict[str, Any]:
        """Return summarized profiler data for optional developer tooling."""

        return self.profiler.developer_snapshot()

    def refresh_developer_text(self) -> str:
        """Return the optional developer view as plain text."""

        return self.profiler.developer_text()

    def refresh_analysis(self) -> dict[str, Any]:
        """Return ordered refresh events and reconstructed call chains."""

        return self.profiler.analysis_snapshot()

    def refresh_analysis_text(self) -> str:
        """Return refresh-chain analysis as a compact text report."""

        return self.profiler.analysis_text()

    def reset_analysis(self) -> None:
        """Clear analysis events while preserving aggregate profile metrics."""

        self.profiler.reset_analysis()

    def refresh_chain_analysis(self) -> dict[str, Any]:
        """Return aggregated statistics for identical refresh-chain structures."""

        return self.profiler.chain_analysis_snapshot()

    def refresh_chain_text(self) -> str:
        """Return aggregated refresh-chain statistics as plain text."""

        return self.profiler.chain_analysis_text()

    def refresh_hotspot_analysis(self) -> dict[str, Any]:
        """Return passive gateway hotspot rankings."""

        return self.profiler.hotspot_analysis_snapshot()

    def refresh_hotspot_text(self) -> str:
        """Return passive gateway hotspot rankings as plain text."""

        return self.profiler.hotspot_analysis_text()

    def refresh_pattern_analysis(self) -> dict[str, Any]:
        """Return passive parent-child refresh transition statistics."""

        return self.profiler.pattern_analysis_snapshot()

    def refresh_pattern_text(self) -> str:
        """Return passive parent-child refresh transitions as plain text."""

        return self.profiler.pattern_analysis_text()

    def canvas(self, *, refresh_layers: bool = True) -> None:
        self._run(
            "canvas",
            lambda: self.app.template_draw_canvas(refresh_layers=refresh_layers),
        )

    def overlay(
        self,
        bg_info: dict[str, Any] | None = None,
        *,
        refresh_layers: bool = True,
        refresh_status: bool = True,
    ) -> None:
        self._run(
            "overlay",
            lambda: self.app.template_update_fields_overlay(
                bg_info=bg_info,
                refresh_layers=refresh_layers,
                refresh_status=refresh_status,
            ),
        )

    def layers(self, *, full: bool = False) -> None:
        def refresh() -> None:
            if not hasattr(self.app, "template_layers_body"):
                return
            if full:
                self.app.template_build_layers_panel()
            else:
                self.app.template_refresh_layers_selection()

        self._run("layers_full" if full else "layers_selection", refresh)

    def properties(self, *, load_values: bool = False) -> None:
        def refresh() -> None:
            if load_values:
                self.app.template_load_selected_properties()
            if hasattr(self.app, "template_props_body"):
                self.app.template_build_properties_panel()

        self._run("properties", refresh)

    def selection(self, *, refresh_properties: bool = True) -> None:
        def refresh() -> None:
            if refresh_properties:
                self.properties(load_values=True)
            self.overlay(refresh_layers=False)
            self.layers(full=False)

        self._run("selection", refresh)
