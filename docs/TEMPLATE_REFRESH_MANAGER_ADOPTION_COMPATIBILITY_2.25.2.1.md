# VADAFOK Studio 2.25.2.1

## RefreshManager Adoption Compatibility

This corrective release restores the established selection refresh wrapper contract.

`template_refresh_selection_ui()` again contains the legacy refresh sequence directly:

1. load selected property values when requested;
2. refresh the cached properties panel;
3. refresh the field overlay without rebuilding layers;
4. update only the existing layer-selection widgets.

The `TemplateRefreshManager` remains available as an architectural foundation, but this
release does not route the stable wrapper through it. This preserves existing structural
and behavioral tests and avoids runtime changes.

No rendering, zoom, drag, snapping, history, persistence, or file-format behavior is
intentionally changed.
