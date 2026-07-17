# 2.25.2.0 — RefreshManager Adoption Phase 1

The Template Editor selection refresh gateway now delegates to
`TemplateRefreshManager.selection()`.

This is an architectural-only adoption step. The manager preserves the legacy
call order and parameters, including the partial Layers refresh and the overlay
refresh with `refresh_layers=False`.

Regression tests cover delegation, absence of duplicate calls, complete refresh
order, and the `refresh_properties=False` path.
