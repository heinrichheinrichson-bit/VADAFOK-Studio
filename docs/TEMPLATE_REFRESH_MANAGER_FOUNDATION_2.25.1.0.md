# Template RefreshManager Foundation – 2.25.1.0

This release introduces `TemplateRefreshManager` as a central gateway for Template Editor refresh operations.

## Scope

- Adds gateways for canvas, overlay, layers, properties, and selection refreshes.
- Routes selection-dependent refreshes through the manager.
- Routes selected-template properties, canvas, and full Layers refreshes through the manager.
- Preserves all existing rendering and widget logic inside `app.py`.

The manager is intentionally a thin coordination layer. It changes architecture, not behavior.
