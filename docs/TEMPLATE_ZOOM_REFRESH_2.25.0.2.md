# VADAFOK Studio 2.25.0.2 – Template Zoom Partial Refresh

This step continues the Template Editor refresh audit without changing its controls or workflows.

## Changes

- Zoom redraws no longer rebuild the Layers panel.
- Resetting pan no longer rebuilds the Layers panel.
- Template background source images are cached and reloaded only when the file path or modification time changes.
- The previous canvas remains visible while the resized replacement image is prepared. The canvas is cleared only immediately before the prepared replacement is drawn.

## Intentionally unchanged

- Smart Snap and Smart Guides
- Field dragging and resizing
- Multi-selection
- Zoom levels and controls
- Pan behavior
- Template data and save format
