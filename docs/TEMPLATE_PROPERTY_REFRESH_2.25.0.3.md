# VADAFOK Studio 2.25.0.3 – Property Refresh Audit

This step continues the Template Editor refresh audit without changing controls or workflows.

## Changes

- Property edits update only the field overlay immediately.
- Full background/canvas redraws are no longer triggered for every key release.
- Property persistence is debounced by 250 ms.
- Layers and status are refreshed once after typing pauses.
- Checkbox changes use the same optimized path.

## Intentionally unchanged

- Property fields and automatic saving
- Smart Snap and Smart Guides
- Drag, resize, zoom, and pan
- Multi-selection
- Template file format
